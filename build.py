import os
import yaml
import shutil
import jinja2
from weasyprint import HTML


# Template defaults
defaults = {
    'labels': None,
}


def read_yaml(filename):
    """Read YAML file and return its content as a dictionary."""
    with open(filename, 'rt') as f:
        return yaml.safe_load(f)


def render_template(template_path, vars):
    """Render a template file with provided variables."""
    with open(template_path, 'rt') as f:
        tpl = jinja2.Template(f.read())
    return tpl.render(**vars)


def copy_static_files(theme_dir, output_dir):
    """Copy non-template static files (like images, css) from the theme directory."""
    def ignored_files(src, names):
        return [name for name in names if name.endswith('.jinja2')]

    shutil.copytree(theme_dir, output_dir, ignore=ignored_files)


def clean_directory(output_dir):
    """Remove the output directory if it exists."""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)


def build_html(data, config, output_dir):
    """Generate the HTML version of the resume."""
    theme_name = config.get('theme', 'default')
    vars = defaults.copy()
    vars.update(data)
    vars['config'] = config

    theme_location = os.path.join('themes', theme_name)
    clean_directory(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    copy_static_files(theme_location, output_dir)

    # Iterate over theme files and render templates
    for filename in os.listdir(theme_location):
        if filename.endswith('.jinja2'):
            html = render_template(os.path.join(theme_location, filename), vars)
            output_filename = filename.replace('.jinja2', '.html')
            with open(os.path.join(output_dir, output_filename), 'wt') as f:
                f.write(html)


def build_pdf(data, config, output_dir):
    """Generate the PDF version of the resume using the HTML output."""
    theme_name = config.get('theme', 'default')
    input_html = os.path.join(output_dir, 'index.html')
    output_pdf = os.path.join(output_dir, config.get('pdf_file', 'resume.pdf'))
    
    # Convert HTML to PDF using WeasyPrint
    HTML(input_html).write_pdf(output_pdf)


def main():
    """Main function to read arguments, process YAML data, and generate output."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate resume from YAML data.")
    parser.add_argument('resume_file', help='Path to the YAML file with resume data')
    parser.add_argument('-o', '--output_dir', default='build', help='Output directory for generated files')
    parser.add_argument('-t', '--theme', default='default', help='Theme to use for the resume')
    parser.add_argument('-f', '--format', choices=['html', 'pdf'], default='html', help='Output format')
    
    args = parser.parse_args()
    
    # Read YAML data
    resume_data = read_yaml(args.resume_file)
    config = resume_data.get('config', {})
    config.setdefault('output_dir', args.output_dir)
    config['theme'] = args.theme
    
    # Generate output based on format
    if args.format == 'html':
        build_html(resume_data, config, args.output_dir)
    elif args.format == 'pdf':
        build_html(resume_data, config, args.output_dir)  # First generate HTML
        build_pdf(resume_data, config, args.output_dir)   # Then convert to PDF


if __name__ == '__main__':
    main()
