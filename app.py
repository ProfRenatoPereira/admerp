import os
import datetime
import math
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from whitenoise import WhiteNoise

app = Flask(__name__)
app.secret_key = 'chave_secreta_pedagogica'
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///simulador_local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CATALOGO_MAQUINAS = {
    'cnc_romi': {'nome': 'Centro de Usinagem CNC ROMI 5X', 'pot': 22.0, 'cons': 15.4, 'vel': '8000', 'avan': '20000', 'comp': 1000, 'diam': 500, 'mnt': 1000, 'preco': 620000.0, 'dep': 5166.66, 'venda': 124000.0, 'operador': 'Carlos Souza (Técnico CNC)', 'custo_op': 0.45, 'salario': 3100.0, 'adic': 930.0, 'vida': 120},
    'prensa_100t': {'nome': 'Prensa Hidráulica Industrial 100T', 'pot': 15.0, 'cons': 10.5, 'vel': '60', 'avan': '1200', 'comp': 800, 'diam': 800, 'mnt': 1500, 'preco': 220000.0, 'dep': 1833.33, 'venda': 44000.0, 'operador': 'Marcos Lima (Meio Oficial)', 'custo_op': 0.22, 'salario': 1850.0, 'adic': 282.40, 'vida': 120},
    'forno_tempera': {'nome': 'Forno de Têmpera Contínua', 'pot': 45.0, 'cons': 38.0, 'vel': '1200°C', 'avan': 'Automático', 'comp': 1500, 'diam': 600, 'mnt': 800, 'preco': 180000.0, 'dep': 1500.0, 'venda': 36000.0, 'operador': 'Aline Dias (Tratadora Térmica)', 'custo_op': 0.40, 'salario': 2900.0, 'adic': 564.80, 'vida': 120},
    'forno_revenimento': {'nome': 'Forno de Revenimento Industrial', 'pot': 30.0, 'cons': 24.0, 'vel': '700°C', 'avan': 'Estático', 'comp': 1200, 'diam': 600, 'mnt': 800, 'preco': 120000.0, 'dep': 1000.0, 'venda': 24000.0, 'operador': 'Pedro Alves (Operador Forno)', 'custo_op': 0.35, 'salario': 2400.0, 'adic': 282.40, 'vida': 120},
    'solda_mig_tig': {'nome': 'Estação de Solda MIG/TIG Industrial', 'pot': 7.5, 'cons': 5.2, 'vel': 'N/A', 'avan': 'Manual', 'comp': 500, 'diam': 0, 'mnt': 300, 'preco': 15000.0, 'dep': 125.0, 'venda': 3000.0, 'operador': 'Bruno Silva (Soldador TIG)', 'custo_op': 0.38, 'salario': 2600.0, 'adic': 564.80, 'vida': 120},
    'compressor_parafuso': {'nome': 'Compressor de Ar de Parafuso', 'pot': 11.0, 'cons': 8.8, 'vel': '10 bar', 'avan': 'Contínuo', 'comp': 600, 'diam': 400, 'mnt': 600, 'preco': 35000.0, 'dep': 291.66, 'venda': 7000.0, 'operador': 'Posto de Apoio / Indireto', 'custo_op': 0.0, 'salario': 0.0, 'adic': 0.0, 'vida': 120},
    'jato_areia': {'nome': 'Jato de Areia Pressurizado', 'pot': 5.5, 'cons': 4.1, 'vel': 'N/A', 'avan': 'Manual', 'comp': 800, 'diam': 600, 'mnt': 400, 'preco': 28000.0, 'dep': 233.33, 'venda': 5600.0, 'operador': 'Auxiliar de Jateamento', 'custo_op': 0.20, 'salario': 1512.0, 'adic': 282.40, 'vida': 120}
}
CATALOGO_MATERIAIS = {
    'tub_mec': {'cod': 'TUB-MEC-ST52', 'nome': 'Tubo Mecânico de Alta Resistência ST52', 'preco': 45.50, 'dim': 'Ø 3 pol x 2000mm', 'vol': 150.0},
    'tar_aco': {'cod': 'TAR-ACO-4140', 'nome': 'Tarugo Redondo Aço Liga SAE 4140', 'preco': 28.90, 'dim': 'Ø 2 pol x 1000mm', 'vol': 300.0},
    'bar_lat': {'cod': 'BAR-LAT-CLA', 'nome': 'Barra de Latão de Fácil Usinagem CLA', 'preco': 55.20, 'dim': 'Ø 1 pol x 3000mm', 'vol': 80.0},
    'chapa_a36': {'cod': 'CHA-ACO-A36', 'nome': 'Chapa de Aço Carbono ASTM A36 3mm', 'preco': 18.50, 'dim': '1000x2000mm', 'vol': 200.0},
    'gas_mig': {'cod': 'INS-GAS-MIG', 'nome': 'Cilindro Mistura Gás Solda Argônio/CO2', 'preco': 120.00, 'dim': 'Cilindro 50L', 'vol': 15.0}
}

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    aprovado = db.Column(db.Integer, default=0)

class InvestimentoImobiliario(db.Model):
    __tablename__ = 'investimentos_imobiliarios'
    id = db.Column(db.Integer, primary_key=True)
    turma_nome = db.Column(db.String(100), nullable=False)
    cidade_regiao = db.Column(db.String(100), nullable=False)
    bairro_imovel = db.Column(db.String(100), nullable=False)
    area_imovel = db.Column(db.Float, nullable=False)
    taxa_selic = db.Column(db.Float, nullable=False)
    valor_imovel_estimado = db.Column(db.Float, nullable=False)
    aluguel_regional = db.Column(db.Float, nullable=False)
    perc_acionistas = db.Column(db.Float, nullable=False)
    capital_inicial_negocio = db.Column(db.Float, default=0.0)
class Maquina(db.Model):
    __tablename__ = 'maquinas'
    id = db.Column(db.Integer, primary_key=True)
    nome_equipamento = db.Column(db.String(100), nullable=False)
    potencia = db.Column(db.Float, nullable=False)
    consumo_eletrico = db.Column(db.Float, nullable=False)
    velocidade = db.Column(db.String(50))
    avanco = db.Column(db.String(50))
    comprimento_max = db.Column(db.Float)
    diametro_max = db.Column(db.Float)
    frequencia_manutencao = db.Column(db.Integer, nullable=False)
    horas_trabalhadas = db.Column(db.Integer, default=0)
    preco_compra = db.Column(db.Float, nullable=False)
    depreciacao_mensal = db.Column(db.Float, nullable=False)
    valor_venda_final = db.Column(db.Float, nullable=False)
    custo_minuto_maquina = db.Column(db.Float, nullable=False)
    operador_nome = db.Column(db.String(100), default="Posto Vago - Aguardando MOD")
    custo_minuto_operador = db.Column(db.Float, default=0.0)
    salario_base = db.Column(db.Float, default=0.0)
    valor_adicionais = db.Column(db.Float, default=0.0)
    turno_trabalho = db.Column(db.String(50), default="Diurno")
    dia_semana = db.Column(db.String(50), default="Regular")
    vida_util_meses = db.Column(db.Integer, default=120)

class Material(db.Model):
    __tablename__ = 'materiais'
    id = db.Column(db.Integer, primary_key=True)
    codigo_material = db.Column(db.String(50), unique=True, nullable=False)
    nome_material = db.Column(db.String(100), nullable=False)
    preco_unidade = db.Column(db.Float, nullable=False)
    dimensoes = db.Column(db.String(50))
    volume_disponivel = db.Column(db.Float, nullable=False)
class RequisicaoCompra(db.Model):
    __tablename__ = 'requisicoes_compras'
    id = db.Column(db.Integer, primary_key=True)
    equipamento_tipo = db.Column(db.String(50), nullable=False)
    especificacao_desejada = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50), default="Pendente em Cotação")
    preco_cotado = db.Column(db.Float, default=0.0)
    potencia_cotada = db.Column(db.Float, default=0.0)
    depreciacao_sugerida = db.Column(db.Float, default=0.0)
    vida_util_sugerida = db.Column(db.Integer, default=120)

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    codigo_produto = db.Column(db.String(50), unique=True, nullable=False)
    nome_produto = db.Column(db.String(100), nullable=False)
    custo_total_fabricacao = db.Column(db.Float, default=0.0)

class EstruturaProduto(db.Model):
    __tablename__ = 'estrutura_produto'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, nullable=False)
    maquina_id = db.Column(db.Integer)
    material_id = db.Column(db.Integer)
    tempo_processo_min = db.Column(db.Float, default=0.0)
    quantidade_material = db.Column(db.Float, default=0.0)
class FormacaoPreco(db.Model):
    __tablename__ = 'formacao_precos'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, unique=True, nullable=False)
    imposto_municipal = db.Column(db.Float, default=0.0)
    imposto_estadual = db.Column(db.Float, default=0.0)
    imposto_federal = db.Column(db.Float, default=0.0)
    margem_lucro = db.Column(db.Float, default=0.0)
    preco_venda_final = db.Column(db.Float, default=0.0)

class EstoqueProduto(db.Model):
    __tablename__ = 'estoque_produtos'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, unique=True, nullable=False)
    quantidade_disponivel = db.Column(db.Float, default=0.0)

class PedidoVenda(db.Model):
    __tablename__ = 'pedidos_vendas'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    desconto_percentual = db.Column(db.Float, default=0.0)
    observacoes = db.Column(db.Text)
    data_pedido = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class OrdemProcesso(db.Model):
    __tablename__ = 'ordens_processo'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, nullable=False)
    numero_operacao = db.Column(db.String(50), nullable=False)
    maquina_name = db.Column(db.String(100), nullable=False)
    codigo_produto = db.Column(db.String(50), nullable=False)
    nome_produto = db.Column(db.String(100), nullable=False)
    data_entrada = db.Column(db.String(50), nullable=False)
    tempo_estimado_min = db.Column(db.Float, nullable=False)
    data_saida = db.Column(db.String(50), nullable=False)
    operador_nome = db.Column(db.String(100), default="Pendente")
    status = db.Column(db.String(50), default="Na Fila")
    custo_operacao = db.Column(db.Float, default=0.0)
with app.app_context():
    db.create_all()
    if not InvestimentoImobiliario.query.first():
        cenario = InvestimentoImobiliario(
            turma_nome='Metalúrgica Modelo S/A - Cenário Base', cidade_regiao='Curitiba CIC',
            bairro_imovel='CIC (Distrito Industrial)', area_imovel=450.00, taxa_selic=11.39,
            valor_imovel_estimado=3825000.00, aluguel_regional=13500.00, perc_acionistas=25.0,
            capital_inicial_negocio=500000.00
        )
        db.session.add(cenario)
        minutos_mes = 44 * 4.33 * 60
        for k, m in CATALOGO_MAQUINAS.items():
            if k in ['cnc_romi', 'prensa_100t', 'forno_tempera']:
                c_mm = (m['dep'] / minutos_mes) + ((m['pot'] * 0.75) / 60) + (13500.00 / minutos_mes)
                nova_maq = Maquina(
                    nome_equipamento=m['nome'], potencia=m['pot'], consumo_eletrico=m['cons'],
                    velocidade=m['vel'], avanco=m['avan'], comprimento_max=m['comp'],
                    diametro_max=m['diam'], frequencia_manutencao=m['mnt'], preco_compra=m['preco'],
                    depreciacao_mensal=m['dep'], valor_venda_final=m['venda'], custo_minuto_maquina=c_mm,
                    operador_nome=m['operador'], custo_minuto_operador=m['custo_op'],
                    salario_base=m['salario'], valor_adicionais=m['adic'], vida_util_meses=m['vida']
                )
                db.session.add(nova_maq)
        for mat in CATALOGO_MATERIAIS.values():
            novo_mat = Material(
                codigo_material=mat['cod'], nome_material=mat['nome'],
                preco_unidade=mat['preco'], dimensoes=mat['dim'], volume_disponivel=mat['vol']
            )
            db.session.add(novo_mat)
        db.session.commit()
def calcular_caixa_disponivel():
    ult_imovel = InvestimentoImobiliario.query.order_by(InvestimentoImobiliario.id.desc()).first()
    if not ult_imovel: return 0.0, 0.0
    capital_inicial = float(ult_imovel.capital_inicial_negocio or 0.0)
    aluguel_fixo = float(ult_imovel.aluguel_regional or 0.0)
    investido_maquinas = db.session.query(db.func.coalesce(db.func.sum(Maquina.preco_compra), 0)).scalar()
    comprado_materiais = db.session.query(db.func.coalesce(db.func.sum(Material.preco_unidade * Material.volume_disponivel), 0)).scalar()
    faturamento = db.session.query(db.func.coalesce(db.func.sum(FormacaoPreco.preco_venda_final * PedidoVenda.quantidade), 0)).join(FormacaoPreco, PedidoVenda.produto_id == FormacaoPreco.produto_id).scalar()
    folha_rh = db.session.query(db.func.coalesce(db.func.sum(Maquina.salario_base + Maquina.valor_adicionais), 0)).filter(Maquina.operador_nome != 'Posto Vago - Aguardando MOD', Maquina.operador_nome != '').scalar()
    caixa_atual = capital_inicial - float(investido_maquinas) - float(comprado_materiais) + float(faturamento) - float(folha_rh) - aluguel_fixo
    return caixa_atual, capital_inicial

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login_validar', methods=['POST'])
def login_validar():
    user_input = request.form.get('username')
    pass_input = request.form.get('password')
    equipe = Usuario.query.filter_by(usuario=user_input).first()
    if equipe and check_password_hash(equipe.senha, pass_input):
        session['logado'] = True
        session['usuario_equipe'] = user_input
        flash('Credenciais validadas com sucesso!', 'success')
    else:
        flash('Usuário ou senha inválidos para esta equipe.', 'danger')
    return redirect(url_for('index'))
@app.route('/professor_painel_secreto')
def professor_painel():
    todas_equipes = Usuario.query.all()
    return render_template('professor.html', usuarios=[{'id': u.id, 'usuario': u.usuario} for u in todas_equipes])

@app.route('/professor/resetar', methods=['POST'])
def professor_resetar():
    user_aluno = request.form.get('username')
    nova_senha = request.form.get('nova_senha')
    equipe = Usuario.query.filter_by(usuario=user_aluno).first()
    if equipe:
        equipe.senha = generate_password_hash(nova_senha)
        db.session.commit()
        flash(f"Mecanismo de Pânico: Senha de '{user_aluno}' alterada para '{nova_senha}'!", 'success')
    return redirect(url_for('professor_painel'))

@app.route('/professor/cadastrar', methods=['POST'])
def professor_cadastrar():
    novo_user = request.form.get('novo_user').strip().lower().replace(" ", "")
    senha_inicial = request.form.get('senha_inicial')
    if Usuario.query.filter_by(usuario=novo_user).first():
        flash("Esse nome de equipe já existe!", "danger")
    else:
        novo_usuario = Usuario(usuario=novo_user, senha=generate_password_hash(senha_inicial))
        db.session.add(novo_usuario)
        db.session.commit()
        flash(f"Equipe '{novo_user}' criada com sucesso!", 'success')
    return redirect(url_for('professor_painel'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/inicializar_simulador', methods=['POST'])
def inicializar_simulador():
    if not session.get('logado'): return redirect(url_for('index'))
    nome_empresa = request.form.get('nome_empresa', 'Empresa Simulada S/A')
    try: capital_inicial = float(request.form.get('capital_inicial', 0))
    except ValueError: capital_inicial = 0.0
    InvestimentoImobiliario.query.delete()
    Maquina.query.delete()
    Material.query.delete()
    Produto.query.delete()
    EstruturaProduto.query.delete()
    FormacaoPreco.query.delete()
    EstoqueProduto.query.delete()
    PedidoVenda.query.delete()
    OrdemProcesso.query.delete()
    RequisicaoCompra.query.delete()
    cenario = InvestimentoImobiliario(
        turma_nome=nome_empresa, cidade_regiao='Não Definido', bairro_imovel='Não Definido',
        area_imovel=0.0, taxa_selic=11.39, valor_imovel_estimado=0.0, aluguel_regional=0.0,
        perc_acionistas=0.0, capital_inicial_negocio=capital_inicial
    )
    db.session.add(cenario)
    db.session.commit()
    return redirect(url_for('estrutura'))
@app.route('/estrutura')
def estrutura():
    if not session.get('logado'): return redirect(url_for('index'))
    registros = InvestimentoImobiliario.query.all()
    caixa, total = calcular_caixa_disponivel()
    return render_template('estrutura.html', taxa_atual=11.39, registros=registros, caixa_disponivel=caixa, capital_inicial=total)

@app.route('/salvar_estrutura', methods=['POST'])
def salvar_estrutura():
    if not session.get('logado'): return redirect(url_for('index'))
    ult_reg = InvestimentoImobiliario.query.order_by(InvestimentoImobiliario.id.desc()).first()
    capital_fixado = float(ult_reg.capital_inicial_negocio) if ult_reg else 0.0
    nova_est = InvestimentoImobiliario(
        turma_nome=request.form.get('turma_nome', 'Grupo Geral'), cidade_regiao=request.form.get('cidade_regiao', 'Curitiba'),
        bairro_imovel=request.form.get('bairro_imovel', 'Centro'), area_imovel=float(request.form.get('area_imovel') or 0),
        taxa_selic=float(request.form.get('taxa_selic') or 11.39), valor_imovel_estimado=float(request.form.get('valor_imovel_estimado') or 0),
        aluguel_regional=float(request.form.get('aluguel_regional') or 0), perc_acionistas=float(request.form.get('perc_acionistas') or 0),
        capital_inicial_negocio=capital_fixado
    )
    db.session.add(nova_est)
    db.session.commit()
    return redirect(url_for('estrutura'))

@app.route('/alterar_estrutura/<int:id>', methods=['POST'])
def alterar_estrutura(id):
    if not session.get('logado'): return redirect(url_for('index'))
    reg = InvestimentoImobiliario.query.get(id)
    if reg:
        reg.turma_nome = request.form.get('turma_nome', 'Grupo Geral')
        reg.cidade_regiao = request.form.get('cidade_regiao', 'Curitiba')
        reg.bairro_imovel = request.form.get('bairro_imovel', 'Centro')
        reg.area_imovel = float(request.form.get('area_imovel') or 0)
        reg.taxa_selic = float(request.form.get('taxa_selic') or 11.39)
        reg.valor_imovel_estimado = float(request.form.get('valor_imovel_estimado') or 0)
        reg.aluguel_regional = float(request.form.get('aluguel_regional') or 0)
        reg.perc_acionistas = float(request.form.get('perc_acionistas') or 0)
        db.session.commit()
    return redirect(url_for('estrutura'))

@app.route('/deletar_estrutura/<int:id>', methods=['POST'])
def deletar_estrutura(id):
    if not session.get('logado'): return redirect(url_for('index'))
    reg = InvestimentoImobiliario.query.get(id)
    if reg:
        db.session.delete(reg)
        db.session.commit()
    return redirect(url_for('estrutura'))

@app.route('/maquinas')
def maquinas():
    if not session.get('logado'): return redirect(url_for('index'))
    m_dados = Maquina.query.all()
    ult = InvestimentoImobiliario.query.order_by(InvestimentoImobiliario.id.desc()).first()
    caixa, total = calcular_caixa_disponivel()
    base = ult.aluguel_regional if ult else 0
    minutos_padrao_mes = 44 * 4.33 * 60
    return render_template('maquinas.html', maquinas=m_dados, custo_minuto_estrutural=base/minutos_padrao_mes if base > 0 else 0, caixa_disponivel=caixa, capital_inicial=total)
@app.route('/salvar_maquina', methods=['POST'])
def salvar_maquina():
    if not session.get('logado'): return redirect(url_for('index'))
    nova_maq = Maquina(
        nome_equipamento=request.form.get('nome_equipamento', 'Equipamento'), potencia=float(request.form.get('potencia') or 0),
        consumo_eletrico=float(request.form.get('consumo_eletrico') or 0), velocidade=request.form.get('velocidade', 'N/A'),
        avanco=request.form.get('avanco', 'N/A'), comprimento_max=float(request.form.get('comprimento_max') or 0),
        diametro_max=float(request.form.get('diametro_max') or 0), frequencia_manutencao=int(request.form.get('frequencia_manutencao') or 500),
        horas_trabalhadas=int(request.form.get('horas_trabalhadas') or 0), preco_compra=float(request.form.get('preco_compra') or 0),
        depreciacao_mensal=float(request.form.get('depreciacao_mensal') or 0), valor_venda_final=float(request.form.get('valor_venda_final') or 0),
        custo_minuto_maquina=float(request.form.get('custo_minuto_maquina') or 0), operador_nome=request.form.get('operador_nome', 'Posto Vago - Aguardando MOD'),
        custo_minuto_operador=float(request.form.get('custo_minuto_operador') or 0.0), salario_base=float(request.form.get('salario_base') or 0.0),
        valor_adicionais=float(request.form.get('valor_adicionais') or 0.0), turno_trabalho=request.form.get('turno', 'Diurno'),
        dia_semana=request.form.get('dia_semana', 'Regular'), vida_util_meses=int(request.form.get('vida_util_meses') or 120)
    )
    db.session.add(nova_maq)
    db.session.commit()
    return redirect(url_for('maquinas'))

@app.route('/alterar_maquina/<int:id>', methods=['POST'])
def alterar_maquina(id):
    if not session.get('logado'): return redirect(url_for('index'))
    maq = Maquina.query.get(id)
    if maq:
        maq.nome_equipamento = request.form.get('nome_equipamento', 'Equipamento')
        maq.potencia = float(request.form.get('potencia') or 0)
        maq.consumo_eletrico = float(request.form.get('consumo_eletrico') or 0)
        maq.velocidade = request.form.get('velocidade', 'N/A')
        maq.avanco = request.form.get('avanco', 'N/A')
        maq.comprimento_max = float(request.form.get('comprimento_max') or 0)
        maq.diametro_max = float(request.form.get('diametro_max') or 0)
        maq.frequencia_manutencao = int(request.form.get('frequencia_manutencao') or 500)
        maq.horas_trabalhadas = int(request.form.get('horas_trabalhadas') or 0)
        maq.preco_compra = float(request.form.get('preco_compra') or 0)
        maq.depreciacao_mensal = float(request.form.get('depreciacao_mensal') or 0)
        maq.valor_venda_final = float(request.form.get('valor_venda_final') or 0)
        maq.custo_minuto_maquina = float(request.form.get('custo_minuto_maquina') or 0)
        maq.operador_nome = request.form.get('operador_nome', 'Posto Vago - Aguardando MOD')
        maq.custo_minuto_operador = float(request.form.get('custo_minuto_operador') or 0.0)
        maq.salario_base = float(request.form.get('salario_base') or 0.0)
        maq.valor_adicionais = float(request.form.get('valor_adicionais') or 0.0)
        maq.turno_trabalho = request.form.get('turno', 'Diurno')
        maq.dia_semana = request.form.get('dia_semana', 'Regular')
        maq.vida_util_meses = int(request.form.get('vida_util_meses') or 120)
        db.session.commit()
    return redirect(url_for('maquinas'))

@app.route('/deletar_maquina/<int:id>', methods=['POST'])
def deletar_maquina(id):
    if not session.get('logado'): return redirect(url_for('index'))
    maq = Maquina.query.get(id)
    if maq:
        db.session.delete(maq)
        db.session.commit()
    return redirect(url_for('maquinas'))

@app.route('/rh')
def rh():
    if not session.get('logado'): return redirect(url_for('index'))
    colaboradores = Maquina.query.filter(Maquina.operador_nome != 'Posto Vago - Aguardando MOD', Maquina.operador_nome != '').all()
    caixa, total = calcular_caixa_disponivel()
    return render_template('rh.html', colaboradores=colaboradores, caixa_disponivel=caixa, capital_inicial=total)

@app.route('/salvar_colaborador', methods=['POST'])
def salvar_colaborador():
    if not session.get('logado'): return redirect(url_for('index'))
    posto_vago = Maquina.query.filter_by(operador_nome='Posto Vago - Aguardando MOD').first()
    if posto_vago:
        posto_vago.operador_nome = request.form.get('nome_completo', 'Colaborador')
        posto_vago.salario_base = float(request.form.get('salario_base') or 0)
        posto_vago.valor_adicionais = float(request.form.get('valor_adicionais') or 0)
        posto_vago.turno_trabalho = request.form.get('turno', 'Diurno')
        posto_vago.dia_semana = request.form.get('dia_semana', 'Regular')
        posto_vago.custo_minuto_operador = float(request.form.get('custo_minuto_operador') or 0)
        db.session.commit()
    else:
        nova_maq = Maquina(
            nome_equipamento='Posto de Apoio / Indireto', potencia=0, consumo_eletrico=0, velocidade='N/A', avanco='N/A',
            comprimento_max=0, diametro_max=0, frequencia_manutencao=9999, preco_compra=0, depreciacao_mensal=0, valor_venda_final=0,
            custo_minuto_maquina=0, operador_nome=request.form.get('nome_completo', 'Colaborador'), custo_minuto_operador=float(request.form.get('custo_minuto_operador') or 0),
            salario_base=float(request.form.get('salario_base') or 0), valor_adicionais=float(request.form.get('valor_adicionais') or 0),
            turno_trabalho=request.form.get('turno', 'Diurno'), dia_semana=request.form.get('dia_semana', 'Regular')
        )
        db.session.add(nova_maq)
        db.session.commit()
    return redirect(url_for('rh'))
@app.route('/imprimir_holerite/<int:id>/<string:tipo>')
def imprimir_holerite(id, tipo):
    if not session.get('logado'): return redirect(url_for('index'))
    col = Maquina.query.get(id)
    if not col or col.operador_nome == 'Posto Vago - Aguardando MOD': return "Colaborador não localizado."
    salario_base = float(col.salario_base or 0.0)
    adicionais = float(col.valor_adicionais or 0.0)
    horas_extras_acumuladas = 1250.00 if col.dia_semana != 'Regular' else 0.0
    titulo_recibo = "RECIBO DE PAGAMENTO MENSAL"
    provento_principal_nome = "Salário Base Nominal"
    provento_principal_valor = salario_base
    if tipo == "ferias":
        titulo_recibo = "RECIBO DE PAGAMENTO DE FÉRIAS (CLT)"
        provento_principal_nome = "Férias Integrais"
        provento_principal_valor = salario_base + (salario_base / 3)
    elif tipo == "decimo":
        titulo_recibo = "RECIBO DE DÉCIMO TERCEIRO SALÁRIO"
        provento_principal_nome = "13º Salário Integral"
        provento_principal_valor = salario_base
    total_proventos = provento_principal_valor + adicionais + horas_extras_acumuladas
    inss = total_proventos * 0.075 if total_proventos <= 1518.00 else ((total_proventos * 0.09) - 22.77 if total_proventos <= 2793.88 else ((total_proventos * 0.12) - 106.59 if total_proventos <= 4190.83 else ((total_proventos * 0.14) - 190.40 if total_proventos <= 8157.41 else 951.64)))
    base_irrf = total_proventos - inss
    irrf = 0.0 if base_irrf <= 2259.20 else ((base_irrf * 0.075) - 169.44 if base_irrf <= 2826.65 else ((base_irrf * 0.15) - 381.44 if base_irrf <= 3751.05 else ((base_irrf * 0.225) - 662.77 if base_irrf <= 4664.68 else (base_irrf * 0.275) - 896.00)))
    vale_transporte = salario_base * 0.06 if col.turno_trabalho == 'Diurno' else 0.0
    total_descontos = inss + irrf + vale_transporte
    valor_liquido = total_proventos - total_descontos
    dados_holerite = {"tipo_recibo": titulo_recibo, "nome": col.operador_nome, "cargo": f"CBO {col.id} - Ativo", "principal_nome": provento_principal_nome, "principal_valor": provento_principal_valor, "adicionais": adicionais, "horas_extras": horas_extras_acumuladas, "total_proventos": total_proventos, "inss": inss, "irrf": irrf, "vt": vale_transporte, "total_descontos": total_descontos, "liquido": valor_liquido}
    return render_template('holerite.html', h=dados_holerite)

@app.route('/orcamentos')
def orcamentos():
    if not session.get('logado'): return redirect(url_for('index'))
    maqs = Maquina.query.all()
    caixa, total = calcular_caixa_disponivel()
    return render_template('orcamentos.html', maquinas=maqs, caixa_disponivel=caixa, capital_inicial=total)

@app.route('/salvar_orcamento_calculado', methods=['POST'])
def salvar_orcamento_calculado():
    if not session.get('logado'): return redirect(url_for('index'))
    tipo = request.form.get('tipo_produto')
    nome_item = request.form.get('nome_item')
    lote = int(request.form.get('lote') or 1)
    preco_final = float(request.form.get('preco_final_calculado') or 0.0)
    sku = f"ORC-{tipo.upper()}-{int(preco_final)%1000}"
    try:
        novo_prod = Produto(codigo_produto=sku, nome_produto=nome_item)
        db.session.add(novo_prod)
        db.session.flush()
        novo_preco = FormacaoPreco(produto_id=novo_prod.id, imposto_municipal=float(request.form.get('iss') or 5), imposto_estadual=float(request.form.get('icms') or 18), imposto_federal=float(request.form.get('federal') or 9.25), margem_lucro=float(request.form.get('margem') or 25), preco_venda_final=preco_final / lote)
        db.session.add(novo_preco)
        novo_ped = PedidoVenda(produto_id=novo_prod.id, quantidade=lote, observacoes="SOB ENCOMENDA - Fila PCP")
        db.session.add(novo_ped)
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(url_for('vendas'))

@app.route('/requisicoes')
def requisicoes():
    if not session.get('logado'): return redirect(url_for('index'))
    reqs = RequisicaoCompra.query.order_by(RequisicaoCompra.id.desc()).all()
    caixa, total = calcular_caixa_disponivel()
    return render_template('requisicoes.html', requisicoes=reqs, caixa_disponivel=caixa, capital_inicial=total)
@app.route('/dar_baixa_op/<int:id>', methods=['POST'])
def dar_baixa_op(id):
    if not session.get('logado'): 
        return redirect(url_for('index'))
    op = OrdemProcesso.query.get(id)
    if op:
        op.operador_nome = request.form.get('operador_nome', 'Operador')
        op.status = "Finalizado"
        db.session.commit()
    return redirect(url_for('pcp'))

@app.route('/imprimir_nf/<int:pedido_id>')
def imprimir_nf(pedido_id):
    if not session.get('logado'): 
        return redirect(url_for('index'))
    ped = db.session.query(
        PedidoVenda, 
        Produto.codigo_produto, 
        Produto.nome_produto, 
        FormacaoPreco.preco_venda_final, 
        FormacaoPreco.imposto_municipal, 
        FormacaoPreco.imposto_estadual, 
        FormacaoPreco.imposto_federal
    ).join(Produto, PedidoVenda.produto_id == Produto.id)\
     .join(FormacaoPreco, Produto.id == FormacaoPreco.produto_id)\
     .filter(PedidoVenda.id == pedido_id).first()
     
    if not ped: 
        return "Nota Fiscal não encontrada."
        
    sub = ped.preco_venda_final * ped.PedidoVenda.quantidade
    v_desc = sub * (ped.PedidoVenda.desconto_percentual / 100.0)
    liq = sub - v_desc
    v_mun = liq * (ped.imposto_municipal / 100.0)
    v_est = liq * (ped.imposto_estadual / 100.0)
    v_fed = liq * (ped.imposto_federal / 100.0)
    
    return render_template(
        'nota_fiscal.html', 
        p=ped, 
        subtotal=sub, 
        v_desconto=v_desc, 
        total_liquido=liq, 
        v_municipal=v_mun, 
        v_estadual=v_est, 
        v_federal=v_fed, 
        total_impostos=v_mun+v_est+v_fed
    )
@app.route('/financeiro')
def financeiro():
    if not session.get('logado'): 
        return redirect(url_for('index'))
    faturamento_bruto = db.session.query(db.func.coalesce(db.func.sum(FormacaoPreco.preco_venda_final * PedidoVenda.quantidade), 0)).join(FormacaoPreco, PedidoVenda.produto_id == FormacaoPreco.produto_id).scalar()
    despesa_pessoal_bruta = db.session.query(db.func.coalesce(db.func.sum(Maquina.salario_base + Maquina.valor_adicionais), 0)).filter(Maquina.operador_nome != 'Posto Vago - Aguardando MOD', Maquina.operador_nome != '').scalar()
    impostos_vendas = db.session.query(db.func.coalesce(db.func.sum((FormacaoPreco.preco_venda_final * PedidoVenda.quantidade) * ((FormacaoPreco.imposto_municipal + FormacaoPreco.imposto_estadual + FormacaoPreco.imposto_federal) / 100.0)), 0)).join(FormacaoPreco, PedidoVenda.produto_id == FormacaoPreco.produto_id).scalar()
    caixa, total = calcular_caixa_disponivel()
    total_encargos = impostos_vendas + (despesa_pessoal_bruta * 0.20)
    return render_template('financeiro.html', faturamento=faturamento_bruto, custo_pessoal=despesa_pessoal_bruta, impostos=total_encargos, saldo_liquido=caixa, caixa_disponivel=caixa, capital_inicial=total)

@app.route('/pagar_dividendos', methods=['POST'])
def pagar_dividendos():
    if not session.get('logado'): 
        return redirect(url_for('index'))
    percentual = float(request.form.get('percentual_lucro' or 25))
    flash(f'Distribuição de {percentual}% dos dividendos processada!', 'success')
    return redirect(url_for('financeiro'))
@app.route('/roi')
def roi():
    if not session.get('logado'): 
        return redirect(url_for('index'))
    v_dados = db.session.query(db.func.coalesce(db.func.sum(FormacaoPreco.preco_venda_final * PedidoVenda.quantidade), 0).label('receita_bruta'), db.func.coalesce(db.func.sum(PedidoVenda.quantidade), 0).label('total_pecas')).join(FormacaoPreco, PedidoVenda.produto_id == FormacaoPreco.produto_id).first()
    invs = db.session.query(db.func.coalesce(db.func.sum(InvestimentoImobiliario.valor_imovel_estimado + InvestimentoImobiliario.capital_inicial_negocio), 0).label('capital_total'), db.func.coalesce(db.func.sum(InvestimentoImobiliario.aluguel_regional), 0).label('aluguel')).first()
    despesa_pessoal = db.session.query(db.func.coalesce(db.func.sum(Maquina.salario_base + Maquina.valor_adicionais), 0)).filter(Maquina.operador_nome != 'Posto Vago - Aguardando MOD', Maquina.operador_nome != '').scalar()
    caixa, total = calcular_caixa_disponivel()
    rec, pecas, cap, aluguel = v_dados.receita_bruta, v_dados.total_pecas, invs.capital_total, invs.aluguel
    sobra = rec - despesa_pessoal - aluguel
    payback_meses = (cap / sobra) if sobra > 0 else 0.0
    return render_template('roi.html', receita=rec, total_pecas=pecas, capital=cap, payback_real=payback_meses, lucro_acionistas=rec*0.25, caixa_disponivel=caixa, capital_inicial=total)

if __name__ == '__main__':
    app.run(debug=True)
