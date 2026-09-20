import re

with open('/home/anshul/Desktop/final-sih-frontend/src/routes/reports.tsx', 'r') as f:
    content = f.read()

old_pdf = 'toast("PDF export is not connected to a document service in this build.")'
new_pdf = 'window.print()'
content = content.replace(old_pdf, new_pdf)

old_share = 'toast("Share links are not connected to a sharing service in this build.")'
new_share = '''(() => {
              if (navigator.share) {
                navigator.share({ title: document.title, url: window.location.href }).catch(() => {});
              } else {
                navigator.clipboard.writeText(window.location.href);
                toast(t("Link copied to clipboard"));
              }
            })()'''
content = content.replace(old_share, new_share)

with open('/home/anshul/Desktop/final-sih-frontend/src/routes/reports.tsx', 'w') as f:
    f.write(content)
