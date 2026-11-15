"""Junta a capa da consolidação e os formulários dos testadores num único PDF.

Uso: python scripts/consolidar_testes.py <pasta> [nome_de_saida.pdf]

A pasta deve ter 00_Capa_Consolidacao.docx e os Formulario_Teste_*.docx já preenchidos (ou os PDFs deles).
Cada .docx é convertido para PDF com o Word (scripts/docx_para_pdf.ps1) e depois todos são unidos, na ordem:
capa e testadores 1, 2, 3... Requer Microsoft Word e a biblioteca pymupdf (pip install pymupdf).
Feche os arquivos no Word antes de rodar.
"""
import pathlib
import subprocess
import sys

import pymupdf

AQUI = pathlib.Path(__file__).resolve().parent


def para_pdf(docx):
    pdf = docx.with_suffix(".pdf")
    if not pdf.exists() or pdf.stat().st_mtime < docx.stat().st_mtime:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        str(AQUI / "docx_para_pdf.ps1"), str(docx), str(pdf)], check=True, timeout=180)
    return pdf


def main():
    pasta = pathlib.Path(sys.argv[1]).resolve()
    saida = pasta / (sys.argv[2] if len(sys.argv) > 2 else "Testes_Usuarios_Consolidado.pdf")
    capa = pasta / "00_Capa_Consolidacao.docx"
    formularios = sorted(f for f in pasta.glob("Formulario_Teste_*.docx") if not f.name.startswith("~$"))
    if not capa.exists() or not formularios:
        sys.exit(f"Preciso de {capa.name} e de pelo menos um Formulario_Teste_*.docx em {pasta}")

    final = pymupdf.open()
    for arquivo in [capa, *formularios]:
        with pymupdf.open(para_pdf(arquivo)) as parte:
            final.insert_pdf(parte)
        print("adicionado:", arquivo.name)
    final.save(saida)
    print(f"Gerado: {saida} ({final.page_count} páginas, {len(formularios)} formulários)")


if __name__ == "__main__":
    main()
