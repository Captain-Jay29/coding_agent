def print_flower():
    flower = r"""
      /\
     /  \
    /    \
   /------\
   |  ()  |
   \      /
    \    /
     \  /
      \/
      ||
      ||
      ||
    """
    # Print the flower in red using ANSI escape codes
    print("\033[91m" + flower + "\033[0m")

if __name__ == "__main__":
    print_flower()
