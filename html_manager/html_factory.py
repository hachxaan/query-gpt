

from typing import Dict, Tuple

from file_management.models import MailingFactory
from html_manager.models import MailingCampaign


class HTMLFactory:
    def __init__(self, data):
        self.data = data 

    def generate_html(self, row: Dict[str, str], mailing_campaign: MailingCampaign, apply_permanent_images: bool) -> str:
        """
        Genera el código HTML a partir de los datos proporcionados.

        Args:
            data (List[Dict[str, str]]): Datos de entrada.

        Returns:
            str: Código HTML generado.
        """
        html_template = """
        <body>
            <center>
                <table align="center" border="0" cellpadding="0" cellspacing="0" height="100%" width="100%" id="bodyTable">
                    <tr>
                        <td align="center" valign="top" id="bodyCell">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" class="templateContainer">
                                {content}
                            </table>
                        </td>
                    </tr>
                </table>
            </center>
        </body>
        """
        section_templates = {
            'h': 'templateHeader',
            'b': 'templateBody',
            'f': 'templateFooter'
        }
        section_contents = {'templateHeader': '', 'templateBody': '', 'templateFooter': ''}
        
        

        white_label = None
        white_label = row['white_label'].lower()
        for key, value in row.items():

            if key != 'white_label' and value:
                prefix, image_name = self.parse_column(value)
                section = section_templates.get(prefix)
                if section:
                    
                    record_file = MailingFactory.objects.filter(white_label=white_label, name=image_name).first()
                    if record_file:
                        href = record_file.href
                    else:
                        href = ''

                    if apply_permanent_images:
                        permanet_sections = MailingFactory.objects.filter(white_label=white_label, permanent=True).order_by('order', 'pk')
                        for permanet_section in permanet_sections:
                            if permanet_section.type == 'header':
                                section_contents['templateHeader'] += self.generate_image_block(white_label, image_name, href, prefix)

                            if permanet_section.type == 'footer':
                                section_contents['templateFooter'] += self.generate_image_block(white_label, image_name, href, prefix)

                        apply_permanent_images = False

                    section_contents[section] += self.generate_image_block(white_label, image_name, href, prefix)
            else:
                white_label = row['white_label'].lower()
        content_html = ''
        for section in ['templateHeader', 'templateBody', 'templateFooter']:
            content_html += f'<tr><td valign="top" id="{section}">{section_contents[section]}</td></tr>'
        return html_template.format(content=content_html)
    
    def parse_column(self, value: str) -> Tuple[str, str]:
        # Encuentra la posición del primer guión
        indice = value.find('-')
        # Divide la cadena en la parte antes del guión y la parte después
        prefix = value[:indice]
        name = value[indice+1:]  # +1 para no incluir el guión en el resultado
        return prefix, name
    
    def generate_image_block(self, company_name: str, image_name: str, href: str, prefix: str) -> str:
        """
        Genera un bloque de imagen HTML.

        Args:
            company_name (str): Nombre de la empresa.
            image_name (str): Nombre de la imagen.
            link (str): Enlace opcional.
            prefix (str): Prefijo que indica la ubicación de la imagen.

        Returns:
            str: Bloque de imagen HTML.
        """
        image_src = f"https://api.accesswages.com/mailing/statics/{company_name}-{prefix}-{image_name}.png"
        return f'''
        <table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnImageBlock" style="min-width:100%;">
            <tbody class="mcnImageBlockOuter">
                <tr>
                    <td valign="top" style="padding:0px" class="mcnImageBlockInner">
                        <table align="left" width="100%" border="0" cellpadding="0" cellspacing="0" class="mcnImageContentContainer" style="min-width:100%;">
                            <tbody>
                                <tr>
                                    <td class="mcnImageContent" valign="top" style="padding-right: 0px; padding-left: 0px; padding-top: 0; padding-bottom: 0; text-align:center;">
                                        <a href="{href}" title="" class="" target="_blank">
                                            <img align="center" alt="" src="{image_src}" width="564" style="max-width:800px; padding-bottom: 0; display: inline !important; vertical-align: bottom;" class="mcnImage">
                                        </a>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            </tbody>
        </table>
        '''
    
    def generate_all_html(self):
        for row in self.data:
            html_code = self.generate_html(row)
            print(html_code)