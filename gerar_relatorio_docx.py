import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def add_page_number(run):
    """Insere um campo XML de numeração de página no Word."""
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Aplica margens internas (padding) às células de uma tabela (em dxa: 1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, color_hex):
    """Define a cor de fundo de uma célula da tabela."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def set_table_borders(table, color_hex="CCCCCC", sz="4", val="single"):
    """Aplica bordas horizontais elegantes ao estilo de tabelas académicas (APA), sem linhas verticais."""
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    
    # Bordas superior, inferior e internas horizontais
    for b in ['top', 'bottom', 'insideH']:
        border = OxmlElement(f'w:{b}')
        border.set(qn('w:val'), val)
        border.set(qn('w:sz'), sz)
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), color_hex)
        tblBorders.append(border)
        
    # Remover bordas laterais e verticais internas
    for b in ['left', 'right', 'insideV']:
        border = OxmlElement(f'w:{b}')
        border.set(qn('w:val'), 'none')
        tblBorders.append(border)
        
    tblPr.append(tblBorders)

def criar_relatorio_docx(caminho_saida="RELATORIO.docx"):
    doc = Document()
    
    # ---------------------------------------------------------------------------
    # Configuração de Página (Formato A4, Margens de 2.5 cm - Normas ABNT/APA)
    # ---------------------------------------------------------------------------
    for section in doc.sections:
        section.page_width = Inches(8.27)  # Largura do A4
        section.page_height = Inches(11.69) # Altura do A4
        section.top_margin = Inches(0.98)   # ~2.5 cm
        section.bottom_margin = Inches(0.98)
        section.left_margin = Inches(0.98)
        section.right_margin = Inches(0.98)
        
        # Configurar cabeçalho e rodapé diferenciados para a primeira página (capa)
        section.different_first_page_header_footer = True
        
        # Configurar cabeçalho padrão das páginas seguintes
        header_p = section.header.paragraphs[0]
        header_p.text = "Relatório Científico: MapReduce Multiprocesso em Python"
        header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        header_p.runs[0].font.name = "Arial"
        header_p.runs[0].font.size = Pt(8.5)
        header_p.runs[0].font.color.rgb = RGBColor(120, 120, 120)
        
        # Configurar rodapé padrão das páginas seguintes (Página X)
        footer_p = section.footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_footer = footer_p.add_run("Página ")
        run_footer.font.name = "Arial"
        run_footer.font.size = Pt(9)
        run_footer.font.color.rgb = RGBColor(120, 120, 120)
        add_page_number(footer_p.add_run())
        footer_p.runs[-1].font.name = "Arial"
        footer_p.runs[-1].font.size = Pt(9)
        footer_p.runs[-1].font.color.rgb = RGBColor(120, 120, 120)

    # ---------------------------------------------------------------------------
    # Configuração de Estilos de Texto Padrão
    # ---------------------------------------------------------------------------
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Arial'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = RGBColor(51, 51, 51) # Cinza carvão escuro
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(6)
    style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Cores Corporativas/Académicas
    COR_PRIMARIA = RGBColor(27, 54, 93)   # Azul Escuro Académico (#1B365D)
    COR_SECUNDARIA = RGBColor(46, 107, 158) # Azul Médio (#2E6B9E)
    COR_TEXTO = RGBColor(51, 51, 51)
    COR_HEX_PRIMARIA = "1B365D"
    COR_HEX_CLARA = "F4F6F9"

    # ---------------------------------------------------------------------------
    # CAPA (PÁGINA DE RUSTO)
    # ---------------------------------------------------------------------------
    # Espaço inicial
    for _ in range(3):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
    
    # Nome da Instituição
    inst_p = doc.add_paragraph()
    inst_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    inst_run = inst_p.add_run("INSTITUTO SUPERIOR DE ENGENHARIA\nDEPARTAMENTO DE ENGENHARIA INFORMÁTICA")
    inst_run.font.name = "Arial"
    inst_run.font.size = Pt(12)
    inst_run.font.bold = True
    inst_run.font.color.rgb = COR_PRIMARIA
    
    # Subtítulo da Unidade Curricular
    uc_p = doc.add_paragraph()
    uc_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    uc_run = uc_p.add_run("Sistemas Distribuídos — Laboratório Prático nº 2")
    uc_run.font.name = "Arial"
    uc_run.font.size = Pt(11)
    uc_run.font.italic = True
    uc_run.font.color.rgb = COR_SECUNDARIA

    # Espaço antes do título
    for _ in range(5):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        
    # TÍTULO PRINCIPAL
    tit_p = doc.add_paragraph()
    tit_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tit_run = tit_p.add_run("RELATÓRIO CIENTÍFICO:\nPROCESSAMENTO DISTRIBUÍDO COM MAPREDUCE MULTIPROCESSO EM PYTHON")
    tit_run.font.name = "Arial"
    tit_run.font.size = Pt(20)
    tit_run.font.bold = True
    tit_run.font.color.rgb = COR_PRIMARIA
    tit_p.paragraph_format.space_after = Pt(12)
    
    # Subtítulo do relatório
    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run("Análise Comparativa de Desempenho e Coerência de Dados\nentre Execuções Sequenciais e Multiprocesso")
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(12)
    sub_run.font.color.rgb = COR_TEXTO
    
    # Espaço antes do autor
    for _ in range(6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        
    # Identificação do Autor
    autor_p = doc.add_paragraph()
    autor_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    autor_run = autor_p.add_run("Autor: Estudante de Engenharia Informática\nOrientador: Corpo Docente de Sistemas Distribuídos")
    autor_run.font.name = "Arial"
    autor_run.font.size = Pt(11)
    autor_run.font.bold = True
    autor_run.font.color.rgb = COR_TEXTO
    
    # Espaço antes do rodapé da capa
    for _ in range(4):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        
    # Localidade e Data
    local_p = doc.add_paragraph()
    local_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    local_run = local_p.add_run("Lisboa, Portugal\nSetembro de 2026")
    local_run.font.name = "Arial"
    local_run.font.size = Pt(10.5)
    local_run.font.color.rgb = RGBColor(100, 100, 100)
    
    # Fim da Capa -> Quebra de página
    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # RESUMO (ABSTRACT)
    # ---------------------------------------------------------------------------
    h_resumo = doc.add_paragraph()
    h_resumo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h_res_run = h_resumo.add_run("RESUMO")
    h_res_run.font.name = "Arial"
    h_res_run.font.size = Pt(14)
    h_res_run.font.bold = True
    h_res_run.font.color.rgb = COR_PRIMARIA
    h_resumo.paragraph_format.space_before = Pt(12)
    h_resumo.paragraph_format.space_after = Pt(12)
    
    resumo_p = doc.add_paragraph()
    resumo_p.add_run(
        "Este trabalho apresenta uma investigação prática sobre o processamento de grandes massas de dados "
        "utilizando o modelo de programação MapReduce em ambientes multiprocesso, simulando nós de computação independentes. "
        "A experiência consiste no desenvolvimento de um sistema de contagem de palavras (Word Count) em linguagem Python, "
        "confrontando uma abordagem puramente sequencial (executada de forma síncrona numa única thread) contra uma abordagem "
        "distribuída que tira partido da biblioteca multiprocessing. A arquitetura foi validada com uma carga de trabalho total "
        "de 24 MiB de dados de texto distribuídos uniformemente por três ficheiros determinísticos de 8 MiB cada. Ambas as estratégias "
        "produziram contagens rigorosamente idênticas (3.253.791 de palavras analisadas, totalizando 70 termos únicos), garantindo "
        "a exatidão matemática do processamento. Os ensaios de desempenho demonstraram um ganho de velocidade (speedup) de "
        "2,09x no modo distribuído em comparação com o sequencial, reduzindo o tempo mediano de processamento de 2,3952 segundos "
        "para 1,1487 segundos. Este ganho, embora significativo, ilustra o impacto prático do overhead introduzido pela "
        "comunicação entre processos (IPC), serialização dos dados (via pickle) e restrições de inicialização no sistema operativo. "
        "Os resultados validam empiricamente os limites impostos pela Lei de Amdahl em sistemas concorrentes locais."
    )
    
    resumo_p.runs[0].font.italic = True
    resumo_p.paragraph_format.space_after = Pt(18)
    
    # Palavras-chave
    kw_p = doc.add_paragraph()
    kw_run_bold = kw_p.add_run("Palavras-chave: ")
    kw_run_bold.font.bold = True
    kw_run_bold.font.size = Pt(10)
    kw_run_text = kw_p.add_run("Sistemas Distribuídos, MapReduce, Multiprocessamento, Desempenho, Speedup, Python.")
    kw_run_text.font.italic = True
    kw_run_text.font.size = Pt(10)
    
    doc.add_page_break()

    # Helper para cabeçalhos estruturados
    def add_heading_1(texto):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(texto)
        run.font.name = "Arial"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = COR_PRIMARIA
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        return p

    def add_heading_2(texto):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(texto)
        run.font.name = "Arial"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = COR_SECUNDARIA
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        return p

    def add_heading_3(texto):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(texto)
        run.font.name = "Arial"
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.italic = True
        run.font.color.rgb = COR_TEXTO
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        return p

    # ---------------------------------------------------------------------------
    # SEÇÃO 1: INTRODUÇÃO
    # ---------------------------------------------------------------------------
    add_heading_1("1. Introdução")
    
    p1_1 = doc.add_paragraph(
        "Na era contemporânea da tecnologia da informação, o volume de dados gerado por utilizadores, sensores e "
        "aplicações cresce a um ritmo exponencial. Processar volumes na escala de Gigabytes, Terabytes ou Petabytes de dados "
        "exige estratégias computacionais que superam as capacidades de sistemas de execução sequencial e centralizado. "
        "Surge, assim, a necessidade incontornável de arquiteturas de sistemas distribuídos e de paralelismo computacional, "
        "onde múltiplos recursos de processamento trabalham em sinergia para solucionar um problema comum."
    )
    
    p1_2 = doc.add_paragraph(
        "Um dos algoritmos de referência na validação e estudo destas tecnologias é a contagem de palavras (Word Count). "
        "Apesar da sua aparente simplicidade, este problema possui características fundamentais que se alinham perfeitamente "
        "à decomposição de dados: o conjunto global de dados pode ser facilmente segmentado em subconjuntos independentes (como ficheiros "
        "ou blocos de texto), processados de forma isolada, e cujos resultados intermédios podem ser consolidados de maneira determinística."
    )
    
    p1_3 = doc.add_paragraph(
        "O presente relatório descreve e analisa os resultados do Laboratório 2, dedicado à simulação e teste de um ecossistema "
        "MapReduce concorrente e multiprocesso em Python. O algoritmo compara a execução sequencial com a execução concorrente. "
        "Cada ficheiro de texto funciona como uma partição lógica atribuída a um processo Map dedicado. Os objetivos nucleares do "
        "trabalho englobam: verificar a viabilidade prática da decomposição MapReduce; quantificar o speedup e a eficiência obtidos; "
        "compreender em detalhe as fontes de overhead decorrentes de IPC (Inter-Process Communication); e consolidar conceitos cruciais de "
        "programação paralela em Python."
    )

    # ---------------------------------------------------------------------------
    # SEÇÃO 2: FUNDAMENTAÇÃO TEÓRICA
    # ---------------------------------------------------------------------------
    add_heading_1("2. Fundamentação Teórica")
    
    p2_desc = doc.add_paragraph(
        "Para fundamentar os resultados experimentais, é de extrema relevância definir os conceitos computacionais "
        "envolvidos, compreendendo as potencialidades e limitações físicas e lógicas da execução paralela."
    )
    
    add_heading_2("2.1. Sistemas Distribuídos e Paralelismo")
    
    p2_1_1 = doc.add_paragraph(
        "Um sistema distribuído pode ser caracterizado como uma coleção de computadores autónomos conectados através de uma rede de "
        "comunicação, que se apresentam ao utilizador final como um único sistema coerente. O objetivo primordial destes sistemas é "
        "permitir a escalabilidade horizontal (adicionar mais máquinas de computação de gama média, em vez de investir em supercomputadores "
        "de custo proibitivo para escalabilidade vertical)."
    )
    
    p2_1_2 = doc.add_paragraph(
        "Em contrapartida, o paralelismo local (multiprocessamento) é exercido dentro de um único sistema físico através da exploração "
        "de CPUs multi-core. Embora os processos executem nos mesmos processadores físicos e partilhem o hardware subjacente, eles podem "
        "funcionar com espaços de memória totalmente disjuntos, simulando com fidelidade o comportamento de nós numa rede distribuída. "
        "O paralelismo divide-se habitualmente em duas classes consoante a natureza do gargalo:"
    )
    
    # Lista com marcadores
    p_bullet1 = doc.add_paragraph(style='List Bullet')
    r_b1 = p_bullet1.add_run("CPU-bound: ")
    r_b1.bold = True
    p_bullet1.add_run("quando o tempo de execução é limitado pela velocidade de cálculo aritmético do processador. É o cenário ideal para paralelismo de processos.")
    p_bullet1.paragraph_format.space_after = Pt(2)
    
    p_bullet2 = doc.add_paragraph(style='List Bullet')
    r_b2 = p_bullet2.add_run("I/O-bound: ")
    r_b2.bold = True
    p_bullet2.add_run("quando o tempo de execução depende primariamente da velocidade de dispositivos de entrada/saída (como disco rígido ou rede). Neste caso, as tarefas frequentemente aguardam em estado dormente, e o paralelismo pode deparar-se com contenção de recursos físicos.")
    p_bullet2.paragraph_format.space_after = Pt(6)

    add_heading_2("2.2. O Modelo MapReduce")
    
    p2_2_1 = doc.add_paragraph(
        "Introduzido pela Google (Dean & Ghemawat, 2004), o MapReduce é um modelo de programação e uma infraestrutura de execução "
        "associada concebida para processar e gerar grandes conjuntos de dados. O utilizador define duas funções principais baseadas "
        "no paradigma funcional:"
    )
    
    p_mr1 = doc.add_paragraph(style='List Bullet')
    r_mr1 = p_mr1.add_run("Fase Map (Mapeamento): ")
    r_mr1.bold = True
    p_mr1.add_run("recebe um registo ou bloco de dados bruto de entrada e processa-o para gerar pares chave-valor intermédios. No contexto deste laboratório, cada processo Map recebe um caminho de ficheiro, lê o seu conteúdo, limpa os tokens e gera um dicionário contendo o par ")
    r_kv1 = p_mr1.add_run("(palavra, quantidade)")
    r_kv1.italic = True
    p_mr1.add_run(".")
    p_mr1.paragraph_format.space_after = Pt(2)
    
    p_mr2 = doc.add_paragraph(style='List Bullet')
    r_mr2 = p_mr2.add_run("Fase Shuffle (Transferência/Agregação): ")
    r_mr2.bold = True
    p_mr2.add_run("agrupa todos os valores associados à mesma chave. Em ambientes de rede reais, esta é a fase mais dispendiosa devido ao tráfego gerado pela redistribuição de dados intermédios entre os nós da rede. Na nossa simulação Python, o Shuffle corresponde à recolha centralizada dos dicionários locais de cada processo Map pelo processo principal.")
    p_mr2.paragraph_format.space_after = Pt(2)
    
    p_mr3 = doc.add_paragraph(style='List Bullet')
    r_mr3 = p_mr3.add_run("Fase Reduce (Redução): ")
    r_mr3.bold = True
    p_mr3.add_run("agrega todos os valores intermédios agrupados para aquela chave. A função de redução condensa os múltiplos valores parciais numa única métrica final (por exemplo, somando as contagens de todas as partições).")
    p_mr3.paragraph_format.space_after = Pt(6)

    add_heading_2("2.3. Concorrência e Paralelismo em Python: O Desafio do GIL")
    
    p2_3_1 = doc.add_paragraph(
        "A linguagem Python, na sua implementação de referência (CPython), possui um mecanismo conhecido como Global Interpreter Lock (GIL). "
        "O GIL é um semáforo que garante que apenas uma thread do SO execute bytecodes do Python de cada vez dentro de um processo único. "
        "Embora isto simplifique significativamente a gestão de memória e evite condições de corrida na contagem de referências do garbage collector, "
        "o GIL impede o paralelismo real de CPU-bound em threads concorrentes, uma vez que estas threads disputam a posse do lock, correndo síncronas sob "
        "um único núcleo lógico de processamento."
    )
    
    p2_3_2 = doc.add_paragraph(
        "A solução padrão em Python para contornar esta limitação e usufruir de múltiplos núcleos físicos é o multiprocessamento, "
        "através da biblioteca padrão multiprocessing. Ao lançar novos processos, cada um opera com o seu próprio interpretador "
        "Python e espaço de memória virtual dedicado, eliminando a contenção do GIL. No entanto, esta autonomia traz novos desafios:"
    )
    
    # Sub-bullets para multiprocessamento
    p_mp1 = doc.add_paragraph(style='List Bullet')
    p_mp1.add_run("Cada processo exige um overhead considerável de inicialização (startup do interpretador, carregamento de módulos e duplicação ou criação de contexto).")
    p_mp1.paragraph_format.space_after = Pt(2)
    p_mp2 = doc.add_paragraph(style='List Bullet')
    p_mp2.add_run("Como não há memória partilhada, qualquer transferência de dados (argumentos enviados para a função Map e os dicionários retornados para o Reduce) necessita de IPC (Inter-Process Communication), que recorre à serialização de objetos via módulo pickle. Este processo de empacotamento e descompactação consome ciclos preciosos de CPU.")
    p_mp2.paragraph_format.space_after = Pt(6)

    add_heading_2("2.4. Métricas de Avaliação de Desempenho")
    
    p2_4_desc = doc.add_paragraph(
        "Para avaliar quantitativamente a eficiência de um algoritmo concorrente em relação à sua versão sequencial, são aplicadas três métricas cruciais:"
    )
    
    # Speedup com fórmula em itálico
    p_s = doc.add_paragraph()
    p_s.paragraph_format.left_indent = Inches(0.4)
    p_s.paragraph_format.space_after = Pt(4)
    run_s_label = p_s.add_run("1. Speedup (Ganho de Velocidade): ")
    run_s_label.bold = True
    p_s.add_run("representa a relação entre o tempo de execução sequencial e o tempo de execução distribuída/paralela. É expresso matematicamente por:\n")
    
    # Equação do Speedup
    p_eq1 = doc.add_paragraph()
    p_eq1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq1.paragraph_format.space_after = Pt(10)
    p_eq1.paragraph_format.space_before = Pt(6)
    eq1_s = p_eq1.add_run("S")
    eq1_s.italic = True
    eq1_s.font.size = Pt(12)
    p_eq1.add_run(" = ")
    eq1_t_seq = p_eq1.add_run("T")
    eq1_t_seq.italic = True
    eq1_t_seq.font.size = Pt(12)
    sub1 = p_eq1.add_run("seq")
    sub1.font.subscript = True
    sub1.font.size = Pt(9)
    p_eq1.add_run(" / ")
    eq1_t_dist = p_eq1.add_run("T")
    eq1_t_dist.italic = True
    eq1_t_dist.font.size = Pt(12)
    sub2 = p_eq1.add_run("dist")
    sub2.font.subscript = True
    sub2.font.size = Pt(9)
    
    # Eficiência
    p_e = doc.add_paragraph()
    p_e.paragraph_format.left_indent = Inches(0.4)
    p_e.paragraph_format.space_after = Pt(4)
    run_e_label = p_e.add_run("2. Eficiência Paralela: ")
    run_e_label.bold = True
    p_e.add_run("mede a fração da capacidade total dos processadores que foi efetivamente convertida em ganho útil de processamento, dada por:\n")
    
    # Equação da Eficiência
    p_eq2 = doc.add_paragraph()
    p_eq2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq2.paragraph_format.space_after = Pt(10)
    p_eq2.paragraph_format.space_before = Pt(6)
    eq2_e = p_eq2.add_run("E")
    eq2_e.italic = True
    eq2_e.font.size = Pt(12)
    p_eq2.add_run(" = ")
    eq2_s = p_eq2.add_run("S")
    eq2_s.italic = True
    eq2_s.font.size = Pt(12)
    p_eq2.add_run(" / ")
    eq2_p = p_eq2.add_run("p")
    eq2_p.italic = True
    eq2_p.font.size = Pt(12)
    p_eq2.add_run("  (onde ")
    eq2_p_var = p_eq2.add_run("p")
    eq2_p_var.italic = True
    p_eq2.add_run(" é o número de processos/workers concorrentes ativos)")

    # Lei de Amdahl
    p_amdahl = doc.add_paragraph()
    p_amdahl.paragraph_format.left_indent = Inches(0.4)
    p_amdahl.paragraph_format.space_after = Pt(6)
    run_a_label = p_amdahl.add_run("3. Lei de Amdahl: ")
    run_a_label.bold = True
    p_amdahl.add_run(
        "postula que o limite teórico do speedup de um algoritmo paralelo é restringido pela sua componente puramente "
        "sequencial (não paralelizável). Se uma fração "
    )
    run_f = p_amdahl.add_run("f")
    run_f.italic = True
    p_amdahl.add_run(" do código pode correr em paralelo e a fração residual ")
    p_1f = p_amdahl.add_run("1 - f")
    p_1f.italic = True
    p_amdahl.add_run(" é estritamente sequencial, o speedup teórico máximo com ")
    run_p_var2 = p_amdahl.add_run("p")
    run_p_var2.italic = True
    p_amdahl.add_run(" processadores é expresso por:\n")

    # Equação da Lei de Amdahl
    p_eq3 = doc.add_paragraph()
    p_eq3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq3.paragraph_format.space_after = Pt(10)
    p_eq3.paragraph_format.space_before = Pt(6)
    eq3_s = p_eq3.add_run("S")
    eq3_s.italic = True
    eq3_s.font.size = Pt(12)
    eq3_sub = p_eq3.add_run("teórico")
    eq3_sub.font.subscript = True
    p_eq3.add_run(" = 1 / [ ( 1 - ")
    eq3_f = p_eq3.add_run("f")
    eq3_f.italic = True
    p_eq3.add_run(" ) + ( ")
    eq3_f2 = p_eq3.add_run("f")
    eq3_f2.italic = True
    p_eq3.add_run(" / ")
    eq3_p = p_eq3.add_run("p")
    eq3_p.italic = True
    p_eq3.add_run(" ) ]")

    p2_4_final = doc.add_paragraph(
        "No nosso caso, a fração sequencial inclui a fase final de Reduce, as operações de escrita em disco, "
        "a medição do tempo e a inicialização de processos. Portanto, mesmo com infinitos núcleos, o tempo "
        "mínimo de processamento estará sempre ancorado no custo destas rotinas sequenciais."
    )

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # SEÇÃO 3: ARQUITETURA E IMPLEMENTAÇÃO
    # ---------------------------------------------------------------------------
    add_heading_1("3. Arquitetura do Sistema e Implementação")
    
    p3_1 = doc.add_paragraph(
        "A arquitetura do protótipo foi projetada focando-se na eficiência de uso de recursos e na adesão fiel ao "
        "paradigma MapReduce. O sistema encontra-se estruturado em dois módulos de script Python independentes e "
        "uma suite de testes automatizados."
    )
    
    add_heading_2("3.1. Geração de Dados Determinística")
    
    p3_gen = doc.add_paragraph(
        "Para testar a infraestrutura computacional de forma robusta e reproduzível, o módulo gerar_dados.py gera "
        "três ficheiros de dados de texto de forma determinística (texto1.txt, texto2.txt e texto3.txt). Cada ficheiro é composto "
        "por sequências repetidas de blocos textuais estáticos de alta dimensão, atingindo um tamanho mínimo de 8.0 MiB por ficheiro. "
        "Ao garantir que todos os ficheiros contêm as mesmas sequências predefinidas de texto, o comportamento estatístico do sistema "
        "é completamente estável e os resultados de contagem tornam-se de fácil verificação cruzada."
    )
    
    add_heading_2("3.2. Funções Nucleares do MapReduce")
    
    p3_func = doc.add_paragraph(
        "A implementação em lab_distribuido.py é estruturada pelas seguintes etapas lógicas:"
    )
    
    p3_func_normalizar = doc.add_paragraph()
    p3_func_normalizar.paragraph_format.left_indent = Inches(0.3)
    p3_func_normalizar.paragraph_format.space_after = Pt(2)
    run_norm_label = p3_func_normalizar.add_run("• normalizar_palavra(token): ")
    run_norm_label.bold = True
    p3_func_normalizar.add_run(
        "Responsável por limpar o ruído tipográfico inerente aos textos. Executa o método casefold() para uniformizar "
        "a capitalização (inclusive caracteres Unicode complexos como acentos) e reconstrói a palavra conservando "
        "apenas os caracteres alfa-numéricos (str.isalnum())."
    )
    
    p3_func_map = doc.add_paragraph()
    p3_func_map.paragraph_format.left_indent = Inches(0.3)
    p3_func_map.paragraph_format.space_after = Pt(2)
    run_map_label = p3_func_map.add_run("• map_function(file_path): ")
    run_map_label.bold = True
    p3_func_map.add_run(
        "Implementa a Fase Map. Recebe o caminho de um único ficheiro e abre-o utilizando a codificação UTF-8. Para garantir "
        "a eficiência de memória (Memory Efficiency), o ficheiro é percorrido de forma incremental (linha a linha), evitando "
        "carregar o ficheiro completo em memória primária de uma só vez (o que causaria problemas de escala em ficheiros gigantes). "
        "Cada palavra é normalizada e registada num objeto collections.Counter, que atua como o dicionário de frequências parciais."
    )
    
    p3_func_reduce = doc.add_paragraph()
    p3_func_reduce.paragraph_format.left_indent = Inches(0.3)
    p3_func_reduce.paragraph_format.space_after = Pt(4)
    run_red_label = p3_func_reduce.add_run("• reduce_function(mapped_results): ")
    run_red_label.bold = True
    p3_func_reduce.add_run(
        "Implementa a Fase Reduce. Recebe um iterador contendo múltiplos dicionários intermédios de frequências de palavras. "
        "Cria um Counter global e consolida todos os dicionários, acumulando as somas das palavras coincidentes através de um "
        "laço otimizado baseado no método Counter.update()."
    )

    add_heading_2("3.3. Estratégias de Processamento")
    
    p3_est_seq = doc.add_paragraph()
    p3_est_seq.paragraph_format.left_indent = Inches(0.3)
    p3_est_seq.paragraph_format.space_after = Pt(2)
    p3_est_seq.add_run("1. Abordagem Sequencial: ").bold = True
    p3_est_seq.add_run(
        "Invocada por processar_sequencial(), executa as fases de Map sequencialmente para cada um dos ficheiros "
        "dentro da mesma thread principal do sistema operativo, alimentando em seguida o reduce_function() de "
        "forma síncrona. Representa a linha de base clássica monotarefa."
    )
    
    p3_est_dist = doc.add_paragraph()
    p3_est_dist.paragraph_format.left_indent = Inches(0.3)
    p3_est_dist.paragraph_format.space_after = Pt(4)
    p3_est_dist.add_run("2. Abordagem Distribuída: ").bold = True
    p3_est_dist.add_run(
        "Invocada por processar_distribuido(), recorre à infraestrutura do multiprocessing.Pool(processes=N) instanciada "
        "como context manager (assegurando o correto encerramento e libertação dos recursos do SO). Utiliza o método pool.map() "
        "para distribuir as funções de mapeamento (map_function) associadas a cada ficheiro pelos processos workers em paralelo. "
        "O processo principal suspende a sua execução até que todas as rotinas Map concluam, após o que executa "
        "a redução (reduce_function) sobre a lista consolidada de resultados."
    )

    add_heading_2("3.4. Mecanismo de Benchmarking e Consistência de Dados")
    
    p3_bench_1 = doc.add_paragraph(
        "O benchmark foi programado de forma rigorosa utilizando um protocolo científico para mitigar o ruído externo inerente ao "
        "sistema operativo (como interrupções de hardware, operações de background e escalonamento de processos):"
    )
    
    p3_bench_list1 = doc.add_paragraph(style='List Bullet')
    p3_bench_list1.add_run("Uso de relógios de precisão: ").bold = True
    p3_bench_list1.add_run("os tempos de execução são capturados por intermédio da biblioteca time.perf_counter(), que recorre a um relógio monotónico de alta resolução, ideal para medir tempos de subsegundo de forma consistente.")
    p3_bench_list1.paragraph_format.space_after = Pt(2)
    
    p3_bench_list2 = doc.add_paragraph(style='List Bullet')
    p3_bench_list2.add_run("Estatística robusta: ").bold = True
    p3_bench_list2.add_run("o benchmark suporta múltiplas repetições consecutivas (parâmetro --repeticoes). Em vez de calcular a média aritmética, o programa calcula a mediana dos tempos. A mediana é imune a picos pontuais causados por atividade de fundo do sistema operativo, garantindo a reprodutibilidade académica.")
    p3_bench_list2.paragraph_format.space_after = Pt(2)
    
    p3_bench_list3 = doc.add_paragraph(style='List Bullet')
    p3_bench_list3.add_run("Controlo de Consistência (Invariabilidade Científica): ").bold = True
    p3_bench_list3.add_run("o programa compara elemento a elemento os dicionários de resultados produzidos pelo modo sequencial e distribuído. Qualquer discrepância lógica ou quantitativa causa a interrupção imediata da execução levantando um RuntimeError. Isto assegura que nenhuma otimização computacional corrompa os dados, preservando a verdade matemática do resultado.")
    p3_bench_list3.paragraph_format.space_after = Pt(6)

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # SEÇÃO 4: METODOLOGIA EXPERIMENTAL
    # ---------------------------------------------------------------------------
    add_heading_1("4. Metodologia Experimental")
    
    p4_1 = doc.add_paragraph(
        "A validação empírica do sistema seguiu um protocolo rigoroso de experimentação científica, cujos parâmetros "
        "são detalhados a seguir para garantir total reprodutibilidade."
    )
    
    add_heading_2("4.1. Configuração do Ambiente de Teste (Hardware e Software)")
    
    p4_hw = doc.add_paragraph(
        "Os testes empíricos foram executados no seguinte ambiente físico e lógico:"
    )
    
    # Lista com parâmetros do HW/SW
    p_hw1 = doc.add_paragraph(style='List Bullet')
    p_hw1.add_run("Sistema Operativo: ").bold = True
    p_hw1.add_run("Windows 11 (versão de 64 bits, build 22631)")
    p_hw1.paragraph_format.space_after = Pt(1)
    
    p_hw2 = doc.add_paragraph(style='List Bullet')
    p_hw2.add_run("Processador: ").bold = True
    p_hw2.add_run("Intel64 Family 6 Model 186 (arquitetura x64 com 12 núcleos lógicos de processamento)")
    p_hw2.paragraph_format.space_after = Pt(1)
    
    p_hw3 = doc.add_paragraph(style='List Bullet')
    p_hw3.add_run("Ambiente Python: ").bold = True
    p_hw3.add_run("Python 3.12.5 (64-bit), executando exclusivamente com bibliotecas padrão da linguagem (multiprocessing, collections, time)")
    p_hw3.paragraph_format.space_after = Pt(1)
    
    p_hw4 = doc.add_paragraph(style='List Bullet')
    p_hw4.add_run("Interface de Execução: ").bold = True
    p_hw4.add_run("PowerShell do Windows no terminal integrado")
    p_hw4.paragraph_format.space_after = Pt(6)

    add_heading_2("4.2. Caracterização dos Dados de Entrada")
    
    p4_data = doc.add_paragraph(
        "Os dados foram previamente gerados pelo script complementar gerar_dados.py com um tamanho alvo de 8.0 MiB "
        "por ficheiro. A tabela seguinte caracteriza os ficheiros de entrada utilizados no benchmark:"
    )
    
    # TABELA 1: Ficheiros de Dados
    t_data = doc.add_table(rows=4, cols=3)
    t_data.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_data)
    
    headers = ["Ficheiro", "Tamanho Real (MiB)", "Natureza do Conteúdo"]
    for idx, header in enumerate(headers):
        cell = t_data.cell(0, idx)
        cell.text = header
        set_cell_background(cell, COR_HEX_PRIMARIA)
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(10)
        
    dados_fich = [
        ("texto1.txt", "8.00 MiB", "Bloco determinístico 1 (Sistemas Distribuídos e Escala)"),
        ("texto2.txt", "8.00 MiB", "Bloco determinístico 2 (Python, Multiprocessing e GIL)"),
        ("texto3.txt", "8.00 MiB", "Bloco determinístico 3 (Speedup, Medição e Rigor)")
    ]
    
    for row_idx, (fich, tam, desc) in enumerate(dados_fich, start=1):
        # Alternar fundo cinza claro para linhas pares
        bg_color = COR_HEX_CLARA if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate([fich, tam, desc]):
            cell = t_data.cell(row_idx, col_idx)
            cell.text = val
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(9.5)
            if col_idx == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            elif col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.runs[0].font.bold = True
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    add_heading_2("4.3. Protocolo Experimental")
    
    p4_protocol = doc.add_paragraph(
        "O benchmark foi iniciado invocando-se o interpretador Python na pasta raiz do projeto. "
        "A fim de maximizar a robustez científica, o teste foi configurado para executar 3 repetições consecutivas. "
        "No modo paralelo, definiu-se a utilização de 3 processos Map concorrentes, correspondendo exatamente "
        "a uma tarefa Map por ficheiro. Esta estratégia limita as tarefas ao número real de ficheiros, evitando o "
        "overhead escusado de criar processos ociosos. Os resultados detalhados foram persistidos num ficheiro JSON "
        "para garantir a integridade dos dados para posterior tratamento estatístico."
    )

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # SEÇÃO 5: RESULTADOS E ANÁLISE EXPERIMENTAL
    # ---------------------------------------------------------------------------
    add_heading_1("5. Resultados e Análise Experimental")
    
    p5_intro = doc.add_paragraph(
        "Nesta secção, são apresentadas as contagens de palavras obtidas e os tempos empíricos registados em laboratório, "
        "procedendo-se à sua posterior análise e discussão teórica."
    )
    
    add_heading_2("5.1. Métricas de Desempenho Registadas")
    
    p5_res_text = doc.add_paragraph(
        "A tabela subsequente apresenta o resumo quantitativo obtido durante as medições medianas obtidas no teste prático:"
    )
    
    # TABELA 2: Resultados do Benchmark
    t_res = doc.add_table(rows=7, cols=2)
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_res)
    
    res_headers = ["Métrica Analisada", "Valor Registado"]
    for idx, header in enumerate(res_headers):
        cell = t_res.cell(0, idx)
        cell.text = header
        set_cell_background(cell, COR_HEX_PRIMARIA)
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(10)
        
    dados_res = [
        ("Volume de Dados Total", "24.00 MiB (3 ficheiros de 8.00 MiB)"),
        ("Processos Map Paralelos", "3 processos ativos"),
        ("Número de Repetições do Ensaio", "3 repetições (mediana selecionada)"),
        ("Tempo Mediano em Execução Sequencial", "2.3952 segundos"),
        ("Tempo Mediano em Execução Distribuída", "1.1487 segundos"),
        ("Speedup Empírico (S = Ts/Td)", "2.09x")
    ]
    
    for row_idx, (metrica, valor) in enumerate(dados_res, start=1):
        bg_color = COR_HEX_CLARA if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate([metrica, valor]):
            cell = t_res.cell(row_idx, col_idx)
            cell.text = val
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(9.5)
            if col_idx == 0:
                p.runs[0].font.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if "segundos" in val or "2.09" in val else WD_ALIGN_PARAGRAPH.LEFT
                
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    p5_res_equal = doc.add_paragraph(
        "Ambos os modos produziram exatamente as mesmas contagens em todas as repetições. "
        "A massa total de texto analisada somou exatamente "
    )
    p5_res_equal.add_run("3.253.791 de palavras").bold = True
    p5_res_equal.add_run(", distribuídas por ")
    p5_res_equal.add_run("70 termos distintos").bold = True
    p5_res_equal.add_run(
        ". O facto de a igualdade de dicionários ter sido mantida assegura "
        "a fidelidade científica do teste."
    )
    
    add_heading_2("5.2. Caracterização Estatística das Palavras mais Frequentes")
    
    p5_freq = doc.add_paragraph(
        "A tabela a seguir apresenta os dez termos mais prevalentes na massa documental determinística:"
    )
    
    # TABELA 3: Top 10 palavras
    t_top = doc.add_table(rows=11, cols=3)
    t_top.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_top)
    
    top_headers = ["Posição", "Palavra (Token Normalizado)", "Contagem Absoluta"]
    for idx, header in enumerate(top_headers):
        cell = t_top.cell(0, idx)
        cell.text = header
        set_cell_background(cell, COR_HEX_PRIMARIA)
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(10)
        
    dados_top = [
        ("1º", "o", "166.683"),
        ("2º", "e", "156.847"),
        ("3º", "em", "120.844"),
        ("4º", "os", "84.841"),
        ("5º", "resultados", "84.841"),
        ("6º", "tempo", "81.842"),
        ("7º", "sistemas", "43.920"),
        ("8º", "distribuídos", "43.920"),
        ("9º", "permitem", "43.920"),
        ("10º", "escalabilidade", "43.920")
    ]
    
    for row_idx, (pos, pal, cont) in enumerate(dados_top, start=1):
        bg_color = COR_HEX_CLARA if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate([pos, pal, cont]):
            cell = t_top.cell(row_idx, col_idx)
            cell.text = val
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(9.5)
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.runs[0].font.bold = True
            elif col_idx == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.runs[0].font.italic = True
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    add_heading_2("5.3. Discussão Teórica e Análise de Overhead")
    
    p5_disc_1 = doc.add_paragraph(
        "A análise detalhada do speedup empírico obtido (2,09x) revela conclusões teóricas de relevo. "
        "Num ambiente perfeitamente paralelo, com 3 processos cooperando num processador multi-core que dispõe de "
        "12 núcleos lógicos livres, poder-se-ia ingenuamente prever um speedup linear teórico de 3,0x. No entanto, "
        "os dados reais demonstram uma eficiência paralela aproximada de 69,7%. A divergência em relação ao "
        "limite ideal deve-se aos seguintes fatores arquitetónicos e físicos:"
    )
    
    # 4 fatores de overhead detalhados
    p_fac1 = doc.add_paragraph()
    p_fac1.paragraph_format.left_indent = Inches(0.3)
    p_fac1.paragraph_format.space_after = Pt(2)
    p_fac1.add_run("1. Custo de IPC e Serialização (Pickle Overhead): ").bold = True
    p_fac1.add_run(
        "Como os processos em Python não partilham o mesmo espaço de memória virtual, os dados têm de ser transmitidos "
        "entre o processo pai e os workers utilizando canais de comunicação do SO (pipes/sockets). Isto exige que "
        "os dicionários contendo dezenas de milhares de palavras e contagens de cada worker sejam totalmente serializados "
        "(convertidos em bytes via pickle) e transmitidos. O processo principal deve receber os bytes e desserializá-los. "
        "Esta conversão bidirecional é altamente intensiva em processamento e representa um custo fixo não-paralelizável."
    )
    
    p_fac2 = doc.add_paragraph()
    p_fac2.paragraph_format.left_indent = Inches(0.3)
    p_fac2.paragraph_format.space_after = Pt(2)
    p_fac2.add_run("2. Custo de Inicialização de Processos (Spawning): ").bold = True
    p_fac2.add_run(
        "No sistema operativo Microsoft Windows, a criação de processos paralelos em Python recorre obrigatoriamente "
        "ao método 'spawn' (ao contrário do 'fork' usado em Unix). O método spawn cria processos totalmente novos, "
        "obrigando à inicialização de um novo interpretador Python, importação dos pacotes necessários e execução "
        "das bibliotecas básicas. Este processo de 'cold-start' consome centenas de milissegundos adicionais antes "
        "que a primeira palavra do ficheiro possa ser efetivamente processada."
    )
    
    p_fac3 = doc.add_paragraph()
    p_fac3.paragraph_format.left_indent = Inches(0.3)
    p_fac3.paragraph_format.space_after = Pt(2)
    p_fac3.add_run("3. Gargalo Sequencial Centralizado (Reduce Phase): ").bold = True
    p_fac3.add_run(
        "Conforme preconizado pela Lei de Amdahl, o processamento total é limitado pela sua parte estritamente sequencial. "
        "Após as tarefas Map concluírem o processamento concorrente, a consolidação final (Reduce) é executada sequencialmente "
        "no processo principal, agregando os dicionários parciais através de somas iterativas docollections.Counter. Esta fase "
        "não beneficia dos múltiplos núcleos, impondo um limite rígido ao speedup global."
    )
    
    p_fac4 = doc.add_paragraph()
    p_fac4.paragraph_format.left_indent = Inches(0.3)
    p_fac4.paragraph_format.space_after = Pt(6)
    p_fac4.add_run("4. Contenção de Recursos de Entrada/Saída (I/O Bottleneck): ").bold = True
    p_fac4.add_run(
        "As tarefas Map realizam operações contínuas de leitura em disco dos ficheiros texto1.txt, texto2.txt e texto3.txt. "
        "Ao contrário de CPUs multi-core, as interfaces físicas de armazenamento (mesmo SSDs modernos) sofrem limitações de "
        "acesso simultâneo de múltiplos descritores de ficheiros concorrentes. A contenção de largura de banda de I/O em disco "
        "pode fazer com que os processos fiquem bloqueados em espera de disco, reduzindo o rendimento efetivo da paralelização."
    )

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # SEÇÃO 6: CONCLUSÕES E TRABALHOS FUTUROS
    # ---------------------------------------------------------------------------
    add_heading_1("6. Conclusões e Trabalhos Futuros")
    
    p6_1 = doc.add_paragraph(
        "O desenvolvimento prático e teste analítico deste sistema MapReduce local multiprocesso permitiu "
        "validar, sob perspetivas empíricas e académicas, os princípios de programação paralela e computação distribuída."
    )
    
    p6_2 = doc.add_paragraph(
        "O experimento comprovou a viabilidade prática da decomposição funcional de problemas de processamento de dados "
        "com o modelo MapReduce. Foi demonstrado que, para grandes volumes de dados textuais (neste caso, 24 MiB de dados de entrada), "
        "o multiprocessamento local compensa o overhead de criação de novos processos no sistema operativo Windows, resultando num "
        "speedup relevante de 2,09x (mediana obtida em ensaio rigoroso). O sistema manteve a exatidão absoluta dos resultados, "
        "demonstrando o determinismo implícito na agregação distribuída."
    )
    
    p6_3 = doc.add_paragraph(
        "No entanto, o estudo das fontes de overhead evidenciou de forma clara os trade-offs envolvidos. O paralelismo local "
        "em Python através de multiprocessamento depara-se com custos intransponíveis de comunicação interprocesso (IPC) devido "
        "à necessidade constante de serialização com pickle, além dos atrasos no spawn de interpretadores e contenção na largura "
        "de banda de leitura concorrente em disco. A Lei de Amdahl revelou-se válida na limitação da escalabilidade linear do "
        "algoritmo, imposta pela fase centralizada de redução e overhead de coordenação."
    )
    
    p6_4 = doc.add_paragraph(
        "Como direções e propostas para trabalhos de investigação futuros, identificam-se os seguintes caminhos:"
    )
    
    p_fut1 = doc.add_paragraph(style='List Bullet')
    p_fut1.add_run("Uso de Filas Assíncronas (Queues): ").bold = True
    p_fut1.add_run("substituir o pool.map() síncrono por estruturas de streaming baseadas em multiprocessing.Queue ou multiprocessing.Pipe para transferir os pares chave-valor continuamente à medida que são lidos, sobrepondo o tempo de Map e Reduce.")
    p_fut1.paragraph_format.space_after = Pt(2)
    
    p_fut2 = doc.add_paragraph(style='List Bullet')
    p_fut2.add_run("Chunk-Based Map Tasks: ").bold = True
    p_fut2.add_run("para ficheiros de dados de dimensão massiva (escala de Gigabytes), projetar mapeadores orientados a blocos físicos de tamanho fixo (e.g. 64 MiB), em vez de mapeadores restritos a um ficheiro por processo.")
    p_fut2.paragraph_format.space_after = Pt(2)
    
    p_fut3 = doc.add_paragraph(style='List Bullet')
    p_fut3.add_run("Implementação de MapReduce de Rede Real: ").bold = True
    p_fut3.add_run("expandir o protótipo para funcionar em sockets ou gRPC distribuído em rede TCP/IP, avaliando o impacto da latência física de rede na fase de Shuffle em comparação com o multiprocessamento local.")
    p_fut3.paragraph_format.space_after = Pt(6)

    # ---------------------------------------------------------------------------
    # REFERÊNCIAS BIBLIOGRÁFICAS
    # ---------------------------------------------------------------------------
    add_heading_1("Referências Bibliográficas")
    
    refs = [
        "DEAN, J.; GHEMAWAT, S. MapReduce: Simplified data processing on large clusters. Communications of the ACM, v. 51, n. 1, p. 107-113, 2008.",
        "TANENBAUM, A. S.; STEEN, M. V. Distributed Systems: Principles and Paradigms. 2. ed. New Jersey: Prentice Hall, 2007.",
        "PYTHON SOFTWARE FOUNDATION. multiprocessing — Process-based parallelism. Documentação Oficial do Python 3.12. Disponível em: <https://docs.python.org/3/library/multiprocessing.html>. Acedido em: 8 set. 2026.",
        "AMDAHL, G. M. Validity of the single processor approach to achieving large scale computing capabilities. In: Proceedings of the AFIPS Spring Joint Computer Conference. Atlantic City: AFIPS Press, 1967. p. 483-485.",
        "MCKINNEY, W. Python for Data Analysis: Data Wrangling with Pandas, NumPy, and IPython. 2. ed. Sebastopol: O'Reilly Media, 2017."
    ]
    
    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4) # Recuo pendente para referências
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run(ref)
        run.font.size = Pt(10)
        run.font.name = "Arial"
        
    # Salvar o documento
    doc.save(caminho_saida)
    print(f"Documento '{caminho_saida}' criado com sucesso.")

if __name__ == "__main__":
    criar_relatorio_docx()
