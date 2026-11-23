import os
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_svg(latex_str, filename, fontsize=32):
    plt.rcParams['svg.fonttype'] = 'path'
    fig = plt.figure(figsize=(10, 2))
    fig.text(0.5, 0.5, latex_str, fontsize=fontsize, ha='center', va='center', color='white')
    fig.patch.set_visible(False)
    plt.axis('off')
    out_path = os.path.join(BASE_DIR, filename)
    plt.savefig(out_path, format='svg', transparent=True, bbox_inches='tight', pad_inches=0.06)
    plt.close(fig)
    print(f"Generated formula SVG: {out_path}")

if __name__ == "__main__":
    generate_svg(r"$(8-2r)^2 + (9-2r)^2 = (2r)^2 \quad \Rightarrow \quad r = 2.5\mathrm{cm}$", "formula_pythagoras.svg")
