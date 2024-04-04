import csv
from typing import List, Dict, Tuple

from file_management.models import MailingFactory

def read_csv(file_path: str) -> List[Dict[str, str]]:
    """
    Lee un archivo CSV y devuelve una lista de diccionarios, cada uno representando una fila.

    Args:
        file_path (str): Ruta al archivo CSV.

    Returns:
        List[Dict[str, str]]: Lista de filas del CSV como diccionarios.
    """
    with open(f"html_manager/{file_path}", mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]
    return data

def generate_html(row: Dict[str, str]) -> str:
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

    
    company_name = row['white_label'].lower()
    for key, value in row.items():
        if key != 'white_label' and value:
            prefix, image_name = parse_column(value)
            href = MailingFactory.objects.filter(white_label=company_name, name=image_name).first().href
            section = section_templates.get(prefix)
            if section:
                section_contents[section] += generate_image_block(company_name, image_name, href, prefix)

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

def generate_image_block(company_name: str, image_name: str, href: str, prefix: str) -> str:
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

# Reemplaza 'your_file.csv' con la ruta al archivo CSV.
data = read_csv('csv/test-carga-4.csv')
for row in data:
    html_code = generate_html(row)
    print(html_code)


class HTMLFactory:
    def __init__(self, file_path: str):
        self.data = self.read_csv(file_path)
    
    def read_csv(self, file_path: str) -> List[Dict[str, str]]:
        """
        Lee un archivo CSV y devuelve una lista de diccionarios, cada uno representando una fila.

        Args:
            file_path (str): Ruta al archivo CSV.

        Returns:
            List[Dict[str, str]]: Lista de filas del CSV como diccionarios.
        """
        with open(f"html_manager/{file_path}", mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            data = [row for row in csv_reader]
        return data
    
    def generate_html(self, row: Dict[str, str]) -> str:
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
        
        company_name = row['white_label'].lower()
        for key, value in row.items():
            if key != 'white_label' and value:
                prefix, image_name, link = self.parse_column(value)
                section = section_templates.get(prefix)
                if section:
                    section_contents[section] += self.generate_image_block(company_name, image_name, link, prefix)
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
    
    def generate_image_block(self, company_name: str, image_name: str, link: str, prefix: str) -> str:
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
                                        <a href="{link}" title="" class="" target="_blank">
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

