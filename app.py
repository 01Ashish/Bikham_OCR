from flask import Flask, request, render_template, jsonify
import os
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename
import glob
import requests
from gpt_prompt import process, process_other, assistant, assistant_other
from prompt import board_certificate_prompt, irs_prompt, bank_letter_prompt, clia_prompt, individual_liability_certificate_prompt, business_liability_certificate_prompt, void_check_prompt, w9_form_prompt, dea_prompt, business_or_facility_license_prompt, aog_prompt, acc_prompt, sdat_prompt, dl_prompt, degree_prompt, pli_prompt, collaborative_agreement_prompt, npdb_prompt, ofac_prompt, sam_prompt, medicare_opt_out_prompt, medicare_certificate_prompt, medicaid_certificate_prompt, oig_prompt, nv_business_license_prompt, ama_prompt,business_license_prompt
from pdf2image import convert_from_path
from pytesseract import image_to_string
import pytesseract
from PIL import Image
app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = 'uploads'
PDF_FOLDER = os.path.join(UPLOAD_FOLDER, 'pdf')
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
CONVERTED_FOLDER = os.path.join(UPLOAD_FOLDER, 'converted')

for folder in [PDF_FOLDER, IMAGE_FOLDER, CONVERTED_FOLDER]:
    os.makedirs(folder, exist_ok=True)
[os.remove(f) for f in glob.glob(os.path.join(PDF_FOLDER, "*"))]
[os.remove(f) for ext in ('*.jpeg', '*.jpg', '*.png') for f in glob.glob(os.path.join(UPLOAD_FOLDER, ext))]
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def convert_pdf_to_images(pdf_path, output_folder):
#     pdf_document = fitz.open(pdf_path)
    
#     for page_num in range(pdf_document.page_count):
#         page = pdf_document.load_page(page_num)
#         pix = page.get_pixmap()
#         image_filename = os.path.join(output_folder, f'page_{page_num + 1}.png')
#         pix.save(image_filename)
#         break
#     return image_filename
val=""
def extract_text_from_document(file_path):
    """
    Extract text from a document, either PDF or image.
    :param file_path: Path to the PDF or image file.
    :return: Extracted text as a single string.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # Check if the file is a PDF
    if file_path.lower().endswith('.pdf'):
        try:
            print(f"Processing PDF: {file_path}")
            
            # Convert PDF to images
            pages = convert_from_path(file_path, dpi=300)
            extracted_text = ""

            # Extract text from each page
            for i, page in enumerate(pages):
                print(f"Processing page {i + 1}/{len(pages)}...")
                text = image_to_string(page)  # Use Tesseract OCR
                extracted_text += text + "\n"  # Append text with a newline
            
            return extracted_text.strip()
        
        except Exception as e:
            raise RuntimeError(f"Error processing PDF: {e}")

    # Check if the file is an image
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        try:
            print(f"Processing Image: {file_path}")
            
            # Open image and extract text
            with Image.open(file_path) as image:
            # Convert image to RGB format to avoid issues with CMYK or grayscale images
                image = image.convert("RGB")

                # Save as a temporary PNG to ensure compatibility
                temp_image_path = "temp_image.png"
                image.save(temp_image_path, format="PNG")

                # Extract text using Tesseract OCR
                extracted_text = image_to_string(temp_image_path)

                # Cleanup temporary image
                os.remove(temp_image_path)
                
            return extracted_text.strip()
        
        except Exception as e:
            raise RuntimeError(f"Error processing image: {e}")
    
    else:
        raise ValueError("Unsupported file type. Please provide a PDF or an image file.")


def prompts_callback(image_file_path,user_input):
    print("entered in image section")
    if user_input=='board_certificate':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path,board_certificate_prompt,ans)
    elif user_input=='irs':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path,irs_prompt,ans)
    elif user_input=='bank_letter':
        ans = extract_text_from_document(image_file_path)
        print(ans)
        result = process(image_file_path,bank_letter_prompt,ans)
    elif user_input=='clia':
        print("entered in clia")
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path,clia_prompt,ans)
    elif user_input=='facility_license':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path, business_or_facility_license_prompt,ans)
    elif user_input=='individual_liability_certificate':
        result = process(image_file_path, individual_liability_certificate_prompt)
    elif user_input=='business_liability_certificate':
        result = process(image_file_path, business_liability_certificate_prompt)
    elif user_input=='void_cheque':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path, void_check_prompt,ans)
    elif user_input=='w9_form':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path, w9_form_prompt,ans)
    elif user_input=='dea':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path, dea_prompt,ans)
    elif user_input=='business_license':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, business_license_prompt,ans)
    elif user_input=='nv_state_business_license':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path, nv_business_license_prompt,ans)
    elif user_input=='articles_of_organization':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path, aog_prompt,ans)
    elif user_input=='accrediation':
        ans = extract_text_from_document(image_file_path)
        ans = extract_text_from_document(image_file_path,ans)
        result = process(image_file_path, acc_prompt,ans)
    elif user_input=='sdat':
        result = process(image_file_path, sdat_prompt)
    elif user_input=='dl':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path, dl_prompt, ans)
    elif user_input=='degree':
        result = process(image_file_path, degree_prompt)
    elif user_input=='professional_license':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path, pli_prompt,ans)
    elif user_input=='collaborative_agreement':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path, collaborative_agreement_prompt,ans)
    elif user_input == 'npdb':
        result = process(image_file_path, npdb_prompt)
    elif user_input == 'ofac':
        result = process(image_file_path, ofac_prompt)
    elif user_input == 'sam':
        result = process(image_file_path, sam_prompt)
    elif user_input == 'medicare_opt_out':
        result = process(image_file_path, medicare_opt_out_prompt)
    elif user_input == 'medicare_certificate':
        result = process(image_file_path, medicare_certificate_prompt)
    elif user_input == 'medicaid_certificate':
        result = process(image_file_path, medicaid_certificate_prompt)
    elif user_input == 'oig':
        result = process(image_file_path, oig_prompt)
    elif user_input == 'ama':
        result = process(image_file_path, ama_prompt)
    else :
        result = process_other(image_file_path,user_input)
    return result

def process_pdf_with_assistant(image_file_path,user_input):
    if user_input=='board_certificate':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path,board_certificate_prompt,ans)
    elif user_input=='irs':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path,irs_prompt,ans)
    elif user_input=='bank_letter':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path,bank_letter_prompt,ans)
    elif user_input=='clia':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path,clia_prompt,ans)
    elif user_input=='facility_license':
        ans = extract_text_from_document(image_file_path)
        result = process(image_file_path, business_or_facility_license_prompt,ans)
    elif user_input=='individual_liability_certificate':
        result = assistant(image_file_path, individual_liability_certificate_prompt)
    elif user_input=='business_liability_certificate':
        result = assistant(image_file_path, business_liability_certificate_prompt)
    elif user_input=='void_cheque':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, void_check_prompt,ans)
    elif user_input=='w9_form':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, w9_form_prompt,ans)
    elif user_input=='dea':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, dea_prompt,ans)
    elif user_input=='business_license':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, business_license_prompt,ans)
    elif user_input=='nv_state_business_license':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, nv_business_license_prompt,ans)
    elif user_input=='articles_of_organization':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, aog_prompt,ans)
    elif user_input=='accrediation':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, acc_prompt,ans)
    elif user_input=='sdat':
        result = assistant(image_file_path, sdat_prompt)
    elif user_input=='dl':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, dl_prompt,ans)
    elif user_input=='degree':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, degree_prompt,ans)
    elif user_input=='professional_license':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, pli_prompt,ans)
    elif user_input=='collaborative_agreement':
        ans = extract_text_from_document(image_file_path)
        result = assistant(image_file_path, collaborative_agreement_prompt,ans)
    elif user_input == 'npdb':
        result = assistant(image_file_path, npdb_prompt)
    elif user_input == 'ofac':
        result = assistant(image_file_path, ofac_prompt)
    elif user_input == 'sam':
        result = assistant(image_file_path, sam_prompt)
    elif user_input == 'medicare_opt_out':
        result = assistant(image_file_path, medicare_opt_out_prompt)
    elif user_input == 'medicare_certificate':
        result = assistant(image_file_path, medicare_certificate_prompt)
    elif user_input == 'medicaid_certificate':
        result = assistant(image_file_path, medicaid_certificate_prompt)
    elif user_input == 'oig':
        result = assistant(image_file_path, oig_prompt)
    elif user_input == 'ama':
        result = assistant(image_file_path, ama_prompt)
    else :
        result = assistant_other(image_file_path,user_input)
    return result

@app.route('/')
def home():
    print("Hello")
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    user_input = request.form['user_input']
    file_url = request.form['file_url']
    try:
        response = requests.get(file_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching file:", e)

    if response.status_code == 200:    
        # Get the content type from the response headers
        content_type = response.headers.get('Content-Type')
        print("content_type: ", content_type)
        if 'pdf' in content_type:
            file_extension = 'pdf'            
        elif 'image' in content_type:
            if 'jpeg' in content_type:
                file_extension = 'jpg'
            elif 'jpg' in content_type:
                file_extension = 'jpg'
            elif 'png' in content_type:
                file_extension = 'png'
        elif 'jpg' in content_type:
            file_extension = 'jpg'
        elif 'png' in content_type:
            file_extension = 'png'
                
        content = response.content
        # pure_name = f'file_{1}'
        # extension = file
        ori_img_new = f"file_{1}.{file_extension}"
        
        file_path = os.path.join(UPLOAD_FOLDER, ori_img_new)
        with open(file_path, 'wb') as file:
            file.write(content)        
        # Save the content to a file
        if file_extension=='pdf':          
            
            #image_file_path = convert_pdf_to_images(os.path.join(save_folder, ori_img_new), CONVERTED_FOLDER)
            result = process_pdf_with_assistant(file_path,user_input)   
        else:            
            result = prompts_callback(file_path,user_input)
        return result
    
    else:
        return "Failed to fetch"
    

if __name__ == '__main__':
    app.run(debug=True,port=8000)
    
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'})
#     user_input = request.form['user_input']
#     file = request.files['file']
    
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'})
    
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)
        
#         if filename.endswith('.pdf'):
            
#             save_folder = PDF_FOLDER
            
#             os.rename(file_path, os.path.join(save_folder, filename))
#             image_file_path = convert_pdf_to_images(os.path.join(save_folder, filename), CONVERTED_FOLDER)
#             result = prompts_callback(image_file_path,user_input)
#             # print(result)
#             [os.remove(f) for f in glob.glob(os.path.join(PDF_FOLDER, "*"))]
#             return result
    
#         else:
#             result = prompts_callback(file_path,user_input)
#             [os.remove(f) for ext in ('*.jpeg', '*.jpg', '*.png') for f in glob.glob(os.path.join(UPLOAD_FOLDER, ext))]
#             # print(result)
#         return result
    
#     return jsonify({'error': 'File type not allowed'})

# if __name__ == '__main__':
#     app.run(debug=True)
