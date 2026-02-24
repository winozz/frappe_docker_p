def before_save(doc, method=None):
    doc.send_welcome_email = 0