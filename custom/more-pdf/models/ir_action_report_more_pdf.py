from odoo import models, _
from odoo.exceptions import UserError

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    #override _render_qweb_pdf to merge pdf and image attachment in one PDFs
    def _render_qweb_pdf(self, docids=None, data=None):
        if self.report_name == 'account.report_original_vendor_bill':
            
            docs = self.env['account.move'].browse(docids)

            #table of stream to merge
            stream_to_merge = []

            for doc in docs:
                # Get attachments for each doc
                attachments = self.env['ir.attachment'].search([('res_model', '=', self.model), ('res_id', '=', doc.id)])
                
                # Process attachments
                for attachment in attachments:
                    # attachement in PDF or image format
                    if attachment.mimetype == 'application/pdf' or attachment.mimetype.startswith('image'):
                        attachment_pdf = self._retrieve_stream_from_attachment(attachment)
                        stream_to_merge.append(attachment_pdf)
            
            #no attachment found
            if len(stream_to_merge) == 0:
                raise UserError(_("No original vendor bills could be found for any of the selected vendor bills."))
            
            #merge stream to PDFs
            return self._merge_pdfs(stream_to_merge), 'pdf'

        return super(IrActionsReport, self)._render_qweb_pdf(docids, data=data)