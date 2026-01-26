import json
from html import escape

def generate_html(json_path, html_path, organization):
    with open(json_path) as f:
        data = json.load(f)["data"]
        
    lines = [
        "<html><head><title>Data Summary</title>",
        "<style>table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #ddd; padding: 8px; } th { background-color: #f2f2f2; }</style>",
        "</head><body>",
        f"<h1>Files Summary</h1><p><strong>Location:</strong> {escape(data['location'])}</p>"
    ]
    
    files = data["files"]
    for cat in ["raw", "processed", "summarised"]:
        if not files[cat]:
            continue
            
        lines.append(f"<h2>{cat.capitalize()} Files</h2>")
        lines.append("<table><tr><th>File Name</th><th>Size (KB)</th><th>Patient ID</th><th>Sample ID</th><th>Path</th><th>Organization</th></tr>")
        
        for f in files[cat]:
            s_id = f["sample_id"]
            if isinstance(s_id, list): s_id = ", ".join(map(str, s_id))
            
            p_id = f["patient_id"]
            if isinstance(p_id, list): p_id = ", ".join(map(str, p_id))

            lines.append("<tr>")
            lines.append(f"<td>{escape(f['file_name'])}</td>")
            lines.append(f"<td>{f['file_size']}</td>")
            lines.append(f"<td>{escape(str(p_id))}</td>")
            lines.append(f"<td>{escape(str(s_id))}</td>")
            lines.append(f"<td>{escape(f['directory'])}</td>")
            lines.append(f"<td>{escape(organization)}</td>")
            lines.append("</tr>")
        lines.append("</table>")
        
    lines.append("</body></html>")
    
    with open(html_path, "w") as f:
        f.write("\n".join(lines))
        
    print(f"HTML report: {html_path}")