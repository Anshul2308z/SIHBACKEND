import re

with open('/home/anshul/Desktop/final-sih-frontend/src/routes/formulation.tsx', 'r') as f:
    content = f.read()

# Replace `{done ? <Panel className="animate-rise p-6">`
old_code = '{done ? <Panel className="animate-rise p-6">'

new_code = '''{done && loading ? (
            <Panel className="p-6">
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-saffron border-t-transparent"></div>
                <p className="mt-4 text-sm font-medium text-foreground">{t("Analyzing formulation guidelines...")}</p>
                <p className="mt-1 text-xs text-muted-foreground">{t("This may take a moment.")}</p>
              </div>
            </Panel>
          ) : done && result ? <Panel className="animate-rise p-6">'''

content = content.replace(old_code, new_code)

with open('/home/anshul/Desktop/final-sih-frontend/src/routes/formulation.tsx', 'w') as f:
    f.write(content)
