import json
from pathlib import Path
from html import escape

def generate_html_from_json(json_path, html_path, organization="WEHI"):
    """
    Dummy implementation that creates a simple HTML file from JSON.
    """
    with open(json_path, "r") as f:
        data = json.load(f)
    summarized_files = data["data"]["files"]["summarised"]
    processed_files = data["data"]["files"]["processed"]
    raw_files = data["data"]["files"]["raw"]
    
    html_lines = [
    "<html>", 
    "<head><title>Data Files Summary</title><link rel='stylesheet' href='output.css'></head>", 
    "<body>", 
    "<h1>Files summary</h1>", 
    f"<p><strong>Location:</strong> {escape(data['data']['location'])}</p>"  # Here shows the directory, meaning the assigned directory for the script
    ]

    # Generating table for Raw files
    html_lines += [
        "<h2>Raw Files</h2>", 
        "<table border='1' cellpadding = '5'",
        "<tr><th>File Name</th><th>File Size (KB)</th><th>Patient ID</th><th>Sample ID</th><th>Directory</th><th>Organization</th></tr>"
    ]

    for file in raw_files:
        sample_ids = file.get("sample_id", [])
        sample_ids = ', '.join(escape(str(s)) for s in sample_ids) if isinstance(sample_ids, list) else escape(str(sample_ids))
        html_lines.append(
            "<tr>"
            f"<td>{escape(file.get('file_name', ''))}</td>"    # file name
            f"<td>{file.get('file_size', '')}</td>"            # file size
            f"<td>{escape(file.get('patient_id', ''))}</td>"   # patient id
            f"<td>{sample_ids}</td>"                           # sample id
            f"<td>{escape(file.get('directory', ''))}</td>"    # file directory (subordinated location of the assigned directory)
            f"<td>{organization}</td>"                         # which organization that the files are from
            "</tr>"
        )
    html_lines.append("</table>")


    # Processed files
    html_lines += [
        "<h2>Processed Files</h2>",
        "<table border='1' cellpadding='5'>",
        "<tr><th>File Name</th><th>File Size (KB)</th><th>Patient ID</th><th>Sample IDs</th><th>Directory</th><th>Organization</th></tr>"
    ]
    for file in processed_files:
        sample_ids = file.get("sample_id", [])
        sample_ids = ', '.join(escape(str(s)) for s in sample_ids) if isinstance(sample_ids, list) else escape(str(sample_ids))
        html_lines.append(
            "<tr>"
            f"<td>{escape(file.get('file_name', ''))}</td>"
            f"<td>{file.get('file_size', '')}</td>"
            f"<td>{escape(file.get('patient_id', ''))}</td>"
            f"<td>{sample_ids}</td>"
            f"<td>{escape(file.get('directory', ''))}</td>"
            f"<td>{organization}</td>"
            "</tr>"
        )
    html_lines.append("</table>")


    # Summarized files
    html_lines += [
        "<h2>Summarised Files</h2>",
        "<table border='1' cellpadding='5'>",
        "<tr><th>File Name</th><th>File Size (KB)</th><th>Patient ID</th><th>Sample IDs</th><th>Directory</th><th>Organization</th></tr>"
    ]
    for file in summarized_files:
        sample_ids = file.get("sample_id", [])
        if isinstance(sample_ids, list):
            sample_ids = ', '.join(escape(str(s)) for s in sample_ids)
        else:
            sample_ids = escape(str(sample_ids))
        html_lines.append(
            "<tr>"
            f"<td>{escape(file.get('file_name', ''))}</td>"
            f"<td>{file.get('file_size', '')}</td>"
            f"<td>{file.get('patient_id', '')}</td>"
            f"<td>{sample_ids}</td>"
            f"<td>{escape(file.get('directory', ''))}</td>"
            f"<td>{organization}</td>"
            "</tr>"
        )
    html_lines.append("</table>")

    # Close HTML
    html_lines += ["</body>", "</html>"]
    
    with open(html_path, "w") as f:
        f.write("\n".join(html_lines))
    print(f"HTML report generated at: {html_path}")