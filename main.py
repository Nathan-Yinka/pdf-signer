import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
from io import BytesIO

app = FastAPI()

# ✅ Enable CORS (allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods
    allow_headers=["*"],  # allow all headers
    expose_headers=["Content-Disposition"],
)

@app.post("/sign-pdf/")
async def sign_pdf(
    pdf_file: UploadFile,
    page: int = Form(...),
    x_percent: float = Form(...),
    y_percent: float = Form(...),
    width_percent: float = Form(...),
    height_percent: float = Form(...),
    signature_image: str = Form(...)
):
    # Decode base64 image
    header, encoded = signature_image.split(",", 1)
    signature_bytes = base64.b64decode(encoded)

    # Read and open PDF
    pdf_bytes = await pdf_file.read()
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Get page size
    page_obj = pdf[page - 1]
    page_width = page_obj.rect.width
    page_height = page_obj.rect.height

    # # Convert % to points
    # x_pt = (x_percent / 100.0) * page_width
    # y_pt = (y_percent / 100.0) * page_height
    # width_pt = (width_percent / 100.0) * page_width
    # height_pt = (height_percent / 100.0) * page_height

    # # Flip Y for PDF coordinate system
    # real_y = page_height - y_pt - height_pt

    # Convert % to points
    x_pt = (x_percent / 100.0) * page_width
    y_pt = (y_percent / 100.0) * page_height
    width_pt = (width_percent / 100.0) * page_width
    height_pt = (height_percent / 100.0) * page_height

    # Adjust x/y if they represent the center of the signature
    x_pt = x_pt - (width_pt / 2)
    y_pt = y_pt - (height_pt / 2)

    # Flip Y for PDF coordinate system
    real_y = page_height - y_pt - height_pt

    # Insert image
    rect = fitz.Rect(x_pt, real_y, x_pt + width_pt, real_y + height_pt)
    page_obj.insert_image(rect, stream=signature_bytes)

    # Return signed PDF
    output = BytesIO()
    pdf.save(output)
    pdf.close()
    output.seek(0)

    return StreamingResponse(output, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=signed.pdf"
    })

# 👇 This lets you run with: python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
