import timeit
import logging
import random
import string

# Setup basic mock objects
class MockItem:
    def __init__(self, content, metadata_):
        self.content = content
        self.metadata_ = metadata_

# Generate mock data
def generate_mock_data(size=1000):
    data = []
    for _ in range(size):
        content = ''.join(random.choices(string.ascii_letters, k=100))
        metadata_ = {"key": ''.join(random.choices(string.ascii_letters, k=10))}
        data.append(MockItem(content, metadata_))
    return data

# Current implementation
def original_implementation(knowledge_results):
    formatted_results = []
    for item in knowledge_results:
        formatted_results.append(
            f"Content: {item.content}\nMetadata: {item.metadata_}"
        )
    return "\n\n".join(formatted_results)

# Optimized implementation
def optimized_implementation(knowledge_results):
    return "\n\n".join(
        f"Content: {item.content}\nMetadata: {item.metadata_}" for item in knowledge_results
    )

if __name__ == "__main__":
    data = generate_mock_data(10000)

    # Measure original
    t_original = timeit.timeit(lambda: original_implementation(data), number=1000)
    print(f"Original: {t_original:.4f} seconds")

    # Measure optimized
    t_optimized = timeit.timeit(lambda: optimized_implementation(data), number=1000)
    print(f"Optimized: {t_optimized:.4f} seconds")

    improvement = ((t_original - t_optimized) / t_original) * 100
    print(f"Improvement: {improvement:.2f}%")
