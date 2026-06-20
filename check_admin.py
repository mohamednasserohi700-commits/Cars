import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'routes', 'admin.py')
with open(path, encoding='utf-8') as f:
    content = f.read()

checks = {
    'outerjoin(Employee)': 'outerjoin(Employee)' in content,
    'outerjoin': 'outerjoin' in content,
    'join(Employee)': 'join(Employee)' in content,
}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin_report.txt')
lines = [f"{k}: {'✅ YES' if v else '❌ NO'}" for k, v in checks.items()]

# Also extract the registrations function
import re
match = re.search(r'def registrations\(\).*?(?=\n@|\nclass |\Z)', content, re.DOTALL)
if match:
    lines.append("\n=== registrations() function ===")
    lines.append(match.group(0)[:800])

result = "\n".join(lines)
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(result)
print(result)
input("\nPress Enter to close...")
