
from flask import Flask, jsonify, request, send_file
import urllib.request      
import html
import unicodedata
import os
import io

from requests import Session
from bs4 import BeautifulSoup as bs
import json
import re

app = Flask(__name__)
sessao = Session()

def normalizacao(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').replace('  ','').replace('\n','').replace('\r','')

def pegaPropriedadePerfil(conteudoHTML, propriedade):
    
    try:
        sitePerfilBS = bs(conteudoHTML, "html.parser")
        bloco = sitePerfilBS.find('span', text = re.compile(propriedade)).find_parent('td')

        objetoIgnorado = bloco.find('span')
        objetoIgnorado.extract()

        return normalizacao(bloco.get_text())

    except:
        return None

def Autenticado(cookie):
    
    sessao = Session()
    sessao.cookies.set("JSESSIONID", cookie)
    sessao.headers.update({'referer': 'https://alunos.cefet-rj.br/matricula/'})

    acesso = sessao.get("https://alunos.cefet-rj.br/aluno/index.action", allow_redirects=False)
    sessao = Session()

    if (acesso.status_code == 302):
        return False
    else:
        return True

@app.route('/perfilFoto/', methods=['GET'])
def perfilFoto():

    sessao = Session()
    
    cookie = request.args.get('cookie')
    sessao.cookies.set("JSESSIONID", cookie)
    
    if (Autenticado(cookie)):
        img_data = sessao.get("https://alunos.cefet-rj.br/aluno/aluno/foto.action").content
        img = io.BytesIO()
        img.write(img_data)
        img.seek(0)

        sessao = Session()

        return send_file(
            img,
            as_attachment=True,
            attachment_filename='imagemPerfil.jpeg',
            mimetype='image/jpeg'
        )
    else:
        return jsonify({
                        "codigo":"400",
                        "msg":"Cookie invalido"
                    })

@app.route('/perfilDadosGerais/', methods=['GET'])
def perfilDadosGerais(): #TODO: finalizar coleta de dados

    sessao = Session()

    cookie = request.args.get('cookie')
    matricula = request.args.get('matricula')

    if (Autenticado(cookie)):

        sessao.cookies.set("JSESSIONID", cookie)
        siteHorarios = sessao.get("https://alunos.cefet-rj.br/aluno/aluno/quadrohorario/menu.action?matricula=" + matricula)
        sitePerfil = sessao.get("https://alunos.cefet-rj.br/aluno/aluno/perfil/perfil.action")

        sessao = Session()
        
        return jsonify({
                        "codigo":"200",
                        "informacoes":{
                            "Matricula":        pegaPropriedadePerfil(siteHorarios.content, '.Matrícula:'),
                            "Curso":            pegaPropriedadePerfil(siteHorarios.content, '.Curso:'),
                            "Periodo Atual":    pegaPropriedadePerfil(siteHorarios.content, '.Período Atual:'),
                            "Nome":             pegaPropriedadePerfil(sitePerfil.content, '.Nome')
                        }
                    })
    else:
        return jsonify({
                        "codigo":"400",
                        "msg":"Cookie invalido"
                    })


        

@app.route('/perfilDados/', methods=['GET'])
def perfilDados(): #TODO: finalizar coleta de dados

    sessao = Session()

    cookie = request.args.get('cookie')
    matricula = request.args.get('matricula')
    sessao.cookies.set("JSESSIONID", cookie)

    if (Autenticado(cookie)):

        siteHorarios = sessao.get("https://alunos.cefet-rj.br/aluno/aluno/quadrohorario/menu.action?matricula=" + matricula)
        sitePerfil = sessao.get("https://alunos.cefet-rj.br/aluno/aluno/perfil/perfil.action")
        sessao = Session()

        return jsonify({
                        "codigo":"200",
                        "academico":{
                            "Matricula":        pegaPropriedadePerfil(siteHorarios.content, '.Matrícula:'),
                            "Curso":            pegaPropriedadePerfil(siteHorarios.content, '.Curso:'),
                            "Periodo Atual":    pegaPropriedadePerfil(siteHorarios.content, '.Período Atual:')
                        },
                        "informacoes":{
                            "Nome":             pegaPropriedadePerfil(sitePerfil.content, '.Nome'),
                            "Nome da Mae":      pegaPropriedadePerfil(sitePerfil.content, '.Nome da Mãe'),
                            "Nome do Pai":      pegaPropriedadePerfil(sitePerfil.content, '.Nome da Pai'),
                            "Nascimento":       pegaPropriedadePerfil(sitePerfil.content, '.Nascimento'),
                            "Sexo":             pegaPropriedadePerfil(sitePerfil.content, '.Sexo'),
                            "Etnia":            pegaPropriedadePerfil(sitePerfil.content, '.Etnia'),
                            "Deficiencia":      pegaPropriedadePerfil(sitePerfil.content, '.Deficiência'),
                            "Tipo Sanguineo":   pegaPropriedadePerfil(sitePerfil.content, '.Tipo Sanguíneo'),
                            "Fator RH":         pegaPropriedadePerfil(sitePerfil.content, '.Fator RH'),
                            "Estado Civil":     pegaPropriedadePerfil(sitePerfil.content, '.Estado Civil'),
                            "Pagina Pessoal":   pegaPropriedadePerfil(sitePerfil.content, '.Página Pessoal'),
                            "Nacionalidade":    pegaPropriedadePerfil(sitePerfil.content, '.Nacionalidade'),
                            "Estado":           pegaPropriedadePerfil(sitePerfil.content, '.Estado'), #TODO: consertar bug, Estado obtem Estado Civil
                            "Naturalidade":     pegaPropriedadePerfil(sitePerfil.content, '.Naturalidade')
                        },
                        "endereco":{
                            "Tipo de endereco":     pegaPropriedadePerfil(sitePerfil.content, '.Tipo de endereço'),
                            "Tipo de logradouro":   pegaPropriedadePerfil(sitePerfil.content, '.Tipo de logradouro'),
                            "Logradouro":           pegaPropriedadePerfil(sitePerfil.content, '.Logradouro'),
                            "Numero":               pegaPropriedadePerfil(sitePerfil.content, '.Número'), #TODO: consertar bug, Numero não é encontrado
                            "Complemento":          pegaPropriedadePerfil(sitePerfil.content, '.Complemento'),
                            "Bairro":               pegaPropriedadePerfil(sitePerfil.content, '.Bairro'),
                            "Pais":                 pegaPropriedadePerfil(sitePerfil.content, '.País'),
                            "Estado":               pegaPropriedadePerfil(sitePerfil.content, '.Estado'), #TODO: consertar bug, Estado obtem Estado Civil
                            "Cidade":               pegaPropriedadePerfil(sitePerfil.content, '.Cidade'),
                            "Distrito":             pegaPropriedadePerfil(sitePerfil.content, '.Distrito'),
                            "CEP":                  pegaPropriedadePerfil(sitePerfil.content, '.CEP'),
                            "Caixa Postal":         pegaPropriedadePerfil(sitePerfil.content, '.Caixa Postal'),
                            "E-mail":               pegaPropriedadePerfil(sitePerfil.content, '.E-mail'),
                            "Tel. Residencial":     pegaPropriedadePerfil(sitePerfil.content, '.Tel. Residencial'),
                            "Tel. Celular":         pegaPropriedadePerfil(sitePerfil.content, '.Tel. Celular'),
                            "Tel. Comercial":       pegaPropriedadePerfil(sitePerfil.content, '.Tel. Comercial'),
                            "Fax":                  pegaPropriedadePerfil(sitePerfil.content, '.Fax')
                        }
                    })
    else:
        return jsonify({
                        "codigo":"400",
                        "msg":"Cookie invalido"
                    })

@app.route('/horarios/', methods=['GET'])
def horarios():
    '''
    sessao = Session()

    cookie = request.args.get('cookie')
    matricula = request.args.get('matricula')

    if (Autenticado(cookie)):
        
    sessao.cookies.set("JSESSIONID", cookie)
    
    siteHorarios = sessao.get("https://alunos.cefet-rj.br/aluno/ajax/aluno/quadrohorario/quadrohorario.action?matricula=" + matricula)
    siteHorariosBS = bs(siteHorarios.content, "html.parser")

    HorariosLinhas = siteHorariosBS.find(id = 'quadrohorario').find_all('tr')

    HorariosLinhasTratado = str(HorariosLinhas).replace("</div></td></div></td></div></td></div></td></div></td></div></td></tr>",'')

    HorariosLinhasTratadoBS = bs(HorariosLinhasTratado, "html.parser")

    print(HorariosLinhas)

    Horarios = []

    for linha in HorariosLinhas:
        HorariosCelulas = linha.find_all('td')

        horario = {}
        horario['intervalo'] = normalizacao(HorariosCelulas[0].get_text())
        print("-------------------------------------------")
        print(HorariosCelulas[0])
        print("-------------------------------------------")

        dias = {}
        dias['Dom'] = normalizacao(HorariosCelulas[1].get_text())
        dias['Seg'] = normalizacao(HorariosCelulas[2].get_text())
        dias['Ter'] = normalizacao(HorariosCelulas[3].get_text())
        dias['Qua'] = normalizacao(HorariosCelulas[4].get_text())
        dias['Qui'] = normalizacao(HorariosCelulas[5].get_text())
        dias['Sex'] = normalizacao(HorariosCelulas[6].get_text())
        dias['Sab'] = normalizacao(HorariosCelulas[7].get_text())

        horario['dias'] = dias

        Horarios.append(horario)

    return jsonify({"horarios":Horarios})

    TrLinhas = HorariosTabela.find_all('tr')

    for itemTrLinhas in TrLinhas:
        
        TdCelula = TrLinhas.find_all('td')
        
        for itemCelula in TdCelula:
            celula = itemCelula.find('a')
            print(celula.text)

    sessao = Session()
'''
    return jsonify({"retorno":"Nao Implementado!"})



@app.route('/geraRelatorio/', methods=['GET'])
def geraRelatorio():
    
    sessao = Session()

    cookie = request.args.get('cookie')
    link = request.args.get('link')

    if (Autenticado(cookie)):
        
        sessao.cookies.set("JSESSIONID", cookie)

        pdf_data = sessao.get("https://alunos.cefet-rj.br/aluno/aluno/relatorio/" + link).content
        pdf = io.BytesIO()
        pdf.write(pdf_data)
        pdf.seek(0)

        sessao = Session()

        return send_file(
            pdf,
            as_attachment=True,
            attachment_filename='relatorio.pdf',
            mimetype='application/pdf'
        )
    else:
        return jsonify({
                        "codigo":"400",
                        "msg":"Cookie invalido"
                    })

@app.route('/listaRelatorios/', methods=['GET'])
def lista_relatorios():
    
    sessao = Session()

    cookie = request.args.get('cookie')
    matricula = request.args.get('matricula')
    
    if (Autenticado(cookie)):

        sessao.cookies.set("JSESSIONID", cookie)
        siteRelatorios = sessao.get("https://alunos.cefet-rj.br/aluno/aluno/relatorio/relatorios.action?matricula=" + matricula)
        siteRelatoriosBS = bs(siteRelatorios.content, "html.parser")

        RelatoriosBrutos = siteRelatoriosBS.find_all('a', {'title':'Relatório em formato PDF'})

        Relatorios = []
        for item in RelatoriosBrutos:
            relatorio = {}
            relatorio['id'] = RelatoriosBrutos.index(item)
            relatorio['nome'] = normalizacao(item.previousSibling)
            relatorio['link'] = item['href'].replace("/aluno/aluno/relatorio/",'')
            Relatorios.append(relatorio)

        sessao = Session()

        return jsonify({
                        "codigo":"200",
                        "relatorios":Relatorios
                    })
    else:
        return jsonify({
                        "codigo":"400",
                        "msg":"Cookie invalido"
                    })

@app.route('/autenticacao/', methods=['GET'])
def autenticacao():

    sessao = Session()

    usuario = request.args.get('usuario')
    senha = request.args.get('senha')

    sessao.headers.update({'referer': 'https://alunos.cefet-rj.br/matricula/'})
    sessao.get("https://alunos.cefet-rj.br/aluno/login.action?error=")

    dados_login = {"j_username":usuario,"j_password":senha}

    sitePost = sessao.post("https://alunos.cefet-rj.br/aluno/j_security_check",data = dados_login)
    sitePostBS = bs(sitePost.content, "html.parser")

    Matricula = sitePostBS.find("input", id="matricula")["value"]
    Cookie = sessao.cookies.get_dict()

    sessao = Session()

    return jsonify({
                        "autenticacao":{
                            "matricula": Matricula,
                            "cookie": Cookie['JSESSIONID']
                        }
                    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
    #app.run(debug=True, host='127.0.0.1', port=port)

#------------------------LINKS-------------------------

#OK - Perfil         - https://alunos.cefet-rj.br/aluno/aluno/perfil/perfil.action
#AlterarSenha   - https://alunos.cefet-rj.br/usuario/usuario/usuario.action?br.com.asten.si.geral.web.spring.interceptors.AplicacaoWebChangeInterceptor.aplicacaoWeb=1
#Matricula      - https://alunos.cefet-rj.br/aluno/aluno/matricula/solicitacoes.action?matricula=           +  siteMatricula
#OK - Relatorio      - https://alunos.cefet-rj.br/aluno/aluno/relatorio/relatorios.action?matricula=             +  siteMatricula
#Horarios       - https://alunos.cefet-rj.br/aluno/aluno/quadrohorario/menu.action?matricula=               +  siteMatricula
#Notas          - https://alunos.cefet-rj.br/aluno/aluno/nota/nota.action?matricula=                        +  siteMatricula
#Comunicacoes   - https://alunos.cefet-rj.br/comunicacoes/noticia/list.action?br.com.asten.si.geral.web.spring.interceptors.AplicacaoWebChangeInterceptor.aplicacaoWeb=1
#Manuais        - https://alunos.cefet-rj.br/aluno/manuais.action