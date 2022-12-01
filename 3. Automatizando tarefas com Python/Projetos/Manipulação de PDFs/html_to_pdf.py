import pdfkit 
import os

options = {
         'page-size': 'A5',
         'margin-top': '0px',
         'margin-right': '0px',
         'margin-bottom': '0px',
         'margin-left': '0px',
         'orientation' : 'landscape',
         'encoding': "UTF-8",
         'dpi': 80,
        #  'page-height': '910px',
        #  'page-width': '1290px',
         'no-outline': True,
    }

css = [
        'static/css/bootstrap.min.css', 
        'static/css/styles.css', 
        'static/css/icons.css', 
        'static/font-awesome6/css/all.css'
        ]


file = open('planner_template.html').read()
del_pattern = open('remove_pattern.html').read()
with open('planner_template.html', 'w') as f:
    f.write(file.replace(del_pattern, ''))

pdfkit.from_file('planner_template.html', '[2022] Digital Planner.pdf', options=options, css=css)
