# loading_animation.py
# Displays a progress bar from 1% to 100% using tqdm

from tqdm import tqdm
import time

def main():
    for i in tqdm(range(1, 101), desc="Loading", ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'):
        time.sleep(0.03)  # Adjust speed as needed
    print("Done!")

if __name__ == "__main__":
    main()
