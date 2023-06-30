from odoo import models, _
from odoo.exceptions import UserError
from PyPDF2 import PdfFileReader, PdfFileMerger
import img2pdf
from PIL import Image
from io import BytesIO

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, docids=None, data=None):
        if self.report_name == 'account.report_original_vendor_bill':
            
            docs = self.env['account.move'].browse(docids)

            #table of PDFFiles object to merge
            pdf_to_merge = []

            for doc in docs:
                # Get attachments for each doc
                attachments = self.env['ir.attachment'].search([('res_model', '=', self.model), ('res_id', '=', doc.id)])
                # Process attachments
                for attachment in attachments:
                    # attachement in PDF format
                    if attachment.mimetype == 'application/pdf':
                        attachment_pdf = PdfFileReader(attachment._full_path(attachment.store_fname))
                        pdf_to_merge.append(attachment_pdf)
                    # attachement in image format
                    if attachment.mimetype.startswith('image'):
                        # convert image to PDF
                        attachment_img = attachment._full_path(attachment.store_fname)
                        attachment_pdf = self._image_to_pdf(attachment_img)
                        pdf_to_merge.append(attachment_pdf)
                    #add PDFFile object to table of PDFs to merge
                    
            
            #no attachment found
            if len(pdf_to_merge) == 0:
                raise UserError(_("No original vendor bills could be found for any of the selected vendor bills."))
            
            #merge PDFs
            merged_pdf = PdfFileMerger(strict=True)
            for pdf in pdf_to_merge:
                merged_pdf.append(pdf, import_bookmarks=False) 
                #import_bookmarks=False to avoid error Unexpected destination '/__WKANCHOR_2'

            #render merged PDF to PDF content
            data_stream = BytesIO()
            merged_pdf.write(data_stream)
            data_stream.seek(0)
            return data_stream.getvalue(), 'pdf'

        return super(IrActionsReport, self)._render_qweb_pdf(docids, data=data)

    def _image_to_pdf(self, attachment_path):
        image = Image.open(attachment_path)
        pdf_bytes = img2pdf.convert(image.filename)
        return PdfFileReader(BytesIO(pdf_bytes))