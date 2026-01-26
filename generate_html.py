import json
from html import escape

STYLE = """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f8; margin: 0; padding: 20px; color: #333; }
    h1, h2, h3 { color: #2c3e50; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
    th { background-color: #2c3e50; color: white; }
    tr:nth-child(even) { background-color: #f9f9f9; }
    tr:hover { background-color: #f1f1f1; }
    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .summary-box { background-color: #ecf0f1; padding: 20px; border-radius: 6px; margin-bottom: 30px; display: flex; justify-content: space-around; }
    .stat { text-align: center; }
    .stat-val { font-size: 24px; font-weight: bold; color: #2c3e50; }
    .stat-label { font-size: 14px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px; }
</style>
"""

def generate_html(json_path, html_path, organization):
    with open(json_path) as f:
        data = json.load(f)["data"]
        
    files = data["files"]
    
    # Calculate stats
    total_files = 0
    total_size = 0
    patients = set()
    samples = set()
    
    for cat in files:
        for f in files[cat]:
            total_files += 1
            total_size += f["file_size"]
            
            p_ids = f["patient_id"] if isinstance(f["patient_id"], list) else [f["patient_id"]]
            for p in p_ids:
                if p: patients.add(p)
                
            s_ids = f["sample_id"] if isinstance(f["sample_id"], list) else [f["sample_id"]]
            for s in s_ids:
                if s: samples.add(s)

    # Build HTML
    lines = [
        "<!DOCTYPE html>",
        "<html><head><title>Data Summary</title>",
        STYLE,
        "</head><body>",
        "<div class='container'>",
        f"<h1>Files Summary</h1><p><strong>Location:</strong> {escape(data['location'])}</p>",
        
        # Summary Box
        "<div class='summary-box'>",
        f"<div class='stat'><div class='stat-val'>{total_files}</div><div class='stat-label'>Total Files</div></div>",
        f"<div class='stat'><div class='stat-val'>{len(patients)}</div><div class='stat-label'>Total Patients</div></div>",
        f"<div class='stat'><div class='stat-val'>{len(samples)}</div><div class='stat-label'>Total Samples</div></div>",
        f"<div class='stat'><div class='stat-val'>{total_size} KB</div><div class='stat-label'>Total Size</div></div>",
        "</div>"
    ]
    
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
        
    lines.append("</div></body></html>")
    
    with open(html_path, "w") as f:
        f.write("\n".join(lines))
        
    print(f"HTML report: {html_path}")