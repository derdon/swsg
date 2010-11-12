from os import path

from clevercss import convert as convert_clevercss


def clevercssfile2cssfile(clevercssfile, cssfile):
    '''render the content of ``clevercssfile`` via ``clevercss.comvert`` and
    write its output into ``cssfile``'''
    ccss_text = clevercssfile.read()
    converted_ccss = convert_clevercss(ccss_text)
    cssfile.write(converted_ccss)


def clevercss(filename, css_filename=None, xhtml_style=False):
    if css_filename is None:
        css_filename = path.splitext(filename)[0] + '.css'
    with open(filename) as input:
        with open(css_filename, 'w') as output:
            clevercssfile2cssfile(input, output)
    return_code = '<link rel="stylesheet" type="text/css" href="{0}">'
    if xhtml_style:
        return_code = return_code[:-1] + ' />'
    return return_code.format(css_filename)
