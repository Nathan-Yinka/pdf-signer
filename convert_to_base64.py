import base64

# Input image file
input_file = "sign.jpeg"

# Output base64 file
output_file = "signature_base64.txt"

# Read and encode image
with open(input_file, "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

# Format with data URI prefix
base64_string = f"data:image/png;base64,{encoded}"

# Save to file
with open(output_file, "w") as out:
    out.write(base64_string)

print(f"✅ Signature base64 saved to: {output_file}")
