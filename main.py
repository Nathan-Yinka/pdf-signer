import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
from io import BytesIO
from PIL import Image

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

@app.post("/sign-pdf/")
async def sign_pdf(
    pdf_file: UploadFile,
    page: int = Form(...),
    x_percent: float = Form(...),  # From left side
    y_percent: float = Form(...),  # From top side
    signature_image: str = Form(...)
):
    # Decode base64 image
    _, encoded = signature_image.split(",", 1)
    signature_bytes = base64.b64decode(encoded)

    # Get image size in pixels
    img = Image.open(BytesIO(signature_bytes))
    img_width_px, img_height_px = img.size

    # Read PDF
    pdf_bytes = await pdf_file.read()
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_obj = pdf[page - 1]
    page_width, page_height = page_obj.rect.width, page_obj.rect.height

    # Scale image proportionally (reasonable width)
    max_img_width_pt = 150
    scale_ratio = max_img_width_pt / img_width_px
    img_width_pt = max_img_width_pt
    img_height_pt = img_height_px * scale_ratio

    # Corrected and simplified Y calculation
    x_pt = (x_percent / 100.0) * page_width
    y_top = page_height * ((y_percent) / 100.0)  # ✅ your correct formula

    # Anchor image from top-left
    rect = fitz.Rect(
        x_pt,
        y_top - img_height_pt,
        x_pt + img_width_pt,
        y_top
    )

    # Insert the image
    page_obj.insert_image(rect, stream=signature_bytes)

    # Return signed PDF
    output = BytesIO()
    pdf.save(output)
    pdf.close()
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=signed.pdf"}
    )

# Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
