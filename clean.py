import os
import re

html_dir = r"c:\Users\ashu1\Downloads\insuramind-ai-fixed\insuramind-ai\frontend"

for root, _, files in os.walk(html_dir):
    for f in files:
        if f.endswith(".html"):
            filepath = os.path.join(root, f)
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
            
            # Remove <style>...</style>
            content = re.sub(r"<style>.*?</style>", "", content, flags=re.DOTALL)
            
            # Remove <div class="animated-bg">...</div>
            content = re.sub(r'<div class="animated-bg">.*?</div>\s*', "", content, flags=re.DOTALL)
            
            # Remove any <canvas>
            content = re.sub(r"<canvas.*?</canvas>\s*", "", content, flags=re.DOTALL)
            
            # Remove <img> tags
            content = re.sub(r"<img[^>]*>\s*", "", content)
            
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
