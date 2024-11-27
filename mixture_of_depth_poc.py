#!/usr/bin/env python3

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
import time

class GatingMechanism(nn.Module):
    """
    A gating mechanism to determine token-specific processing depth.
    """
    def __init__(self, hidden_dim, max_depth):
        super().__init__()
        self.gate = nn.Linear(hidden_dim, max_depth)

    def forward(self, x):
        """
        Predicts depth probabilities for each token.
        Args:
            x: Token embeddings [batch_size, seq_len, hidden_dim]
        Returns:
            depth_probs: Probabilities for each depth [batch_size, seq_len, max_depth]
        """
        logits = self.gate(x)  # [batch_size, seq_len, max_depth]
        depth_probs = F.softmax(logits, dim=-1)
        return depth_probs


class MixtureOfDepths(nn.Module):
    """
    Mixture of Depths model with dynamic routing through transformer layers.
    """
    def __init__(self, llama_model, max_depth):
        super().__init__()
        self.llama = llama_model
        self.hidden_dim = self.llama.config.hidden_size
        self.max_depth = max_depth

        # Gating mechanism to decide depth dynamically
        self.gating_mechanism = GatingMechanism(self.hidden_dim, max_depth)

        # Additional transformer layers for MoD
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=self.hidden_dim,
                nhead=8,
                dim_feedforward=self.hidden_dim * 4,
                dropout=0.1,
            )
            for _ in range(max_depth)
        ])

    def forward(self, input_ids, attention_mask):
        """
        Forward pass with dynamic depth adjustment.
        Args:
            input_ids: Token IDs [batch_size, seq_len]
            attention_mask: Attention mask [batch_size, seq_len]
        Returns:
            outputs: Final output embeddings [batch_size, seq_len, hidden_dim]
        """
        # Get embeddings from LLaMA's embedding layer
        llama_outputs = self.llama(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True)
        embeddings = llama_outputs.hidden_states[-1]  # Last hidden state

        # Predict depth probabilities
        depth_probs = self.gating_mechanism(embeddings)  # [batch_size, seq_len, max_depth]

        outputs = embeddings
        accumulated_probs = torch.ones_like(depth_probs[:, :, 0])  # Tracks remaining token probabilities

        for depth, layer in enumerate(self.layers):
            active_tokens = accumulated_probs > 0.1  # Threshold for active tokens
            if not active_tokens.any():
                break

            outputs = layer(outputs.permute(1, 0, 2))  # Permute for PyTorch Transformer Layer
            outputs = outputs.permute(1, 0, 2)  # Back to [batch_size, seq_len, hidden_dim]

            prob_to_exit = depth_probs[:, :, depth]
            accumulated_probs *= (1 - prob_to_exit)

        return outputs


def compare_models(vanilla_model, mod_model, tokenizer, query):
    """
    Compare vanilla and MoD models on a single query.
    Args:
        vanilla_model: The vanilla LLaMA model
        mod_model: The Mixture of Depths LLaMA model
        tokenizer: Tokenizer for input
        query: Input query string
    """
    # Tokenize input
    inputs = tokenizer(query, return_tensors="pt", padding=True, truncation=True)

    # Run Vanilla Model
    start_time = time.time()
    vanilla_outputs = vanilla_model(**inputs)
    vanilla_time = time.time() - start_time

    # Run Mixture of Depths Model
    start_time = time.time()
    mod_outputs = mod_model(inputs["input_ids"], inputs["attention_mask"])
    mod_time = time.time() - start_time

    # Decode outputs
    vanilla_text = tokenizer.decode(torch.argmax(vanilla_outputs.logits, dim=-1)[0])
    mod_text = tokenizer.decode(torch.argmax(mod_outputs, dim=-1)[0])

    print("\nQuery:", query)
    print("\nVanilla Model Output:", vanilla_text)
    print(f"Vanilla Inference Time: {vanilla_time:.4f}s")
    print("\nMixture of Depths Model Output:", mod_text)
    print(f"Mixture of Depths Inference Time: {mod_time:.4f}s")


def main():
    # Load LLaMA tokenizer and models
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/LLaMA-3.1")
    vanilla_model = AutoModelForCausalLM.from_pretrained("meta-llama/LLaMA-3.1")
    mod_model = MixtureOfDepths(vanilla_model, max_depth=4)

    # Example queries
    queries = [
        "What is artificial intelligence?",
        "Explain quantum mechanics in simple terms.",
        "Describe the differences between convolutional neural networks and recurrent neural networks."
    ]

    for query in queries:
        compare_models(vanilla_model, mod_model, tokenizer, query)


if __name__ == "__main__":
    main()