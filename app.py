import io
import time
import pandas as pd
import streamlit as st
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def clicarNextPageButtonSePossivel():
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.LINK_TEXT, "Próxima Página >"))).click()
        print('clicou')
        return True
    except:
        return False

PATH = "/chromedriver.exe"

# streamlits
st.set_page_config(
   page_title="AreaInsightas",
   page_icon="🧊",
   layout="wide",
   initial_sidebar_state="expanded",
)
st.image("https://linkages.com.br/wp-content/uploads/2021/10/Proposta_3_Logo-Linkages_sem_Fundo-1.png", width=200)
st.title("AreaInsight")
imobiliariaSelecionada = st.selectbox(
    'Selecione uma imobiliária abaixo: ', ('Escolha uma...', 'Vivareal', 'Zapimóveis'))

if(imobiliariaSelecionada == 'Vivareal'):
    url = st.text_input('Insira o link da busca realizada: ',
                        placeholder='Cole aqui...')
    if(url):
        if(url.startswith("https://www.vivareal.com.br/")):
            linksTerrenos = []
            iniciarButton = st.button('Iniciar coleta de dados')
            if(iniciarButton):
                start_time = time.time()
                options = webdriver.ChromeOptions() 
                options.add_argument('start-maximized')
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.ID, "cookie-notifier-cta"))).click()
                # encontrar nmr de páginas e anuncios
                with st.spinner('Buscando quantidade de anúncios...'):
                    time.sleep(5)
                    elementosTerrenos = driver.find_elements(
                        By.XPATH, "//a[@class='property-card__content-link js-card-title']")
                    for terreno in elementosTerrenos:
                        linksTerrenos.append(terreno.get_attribute('href'))
                    qtdPaginas = 1
                    while clicarNextPageButtonSePossivel():
                        time.sleep(6)
                        qtdPaginas += 1
                        elementosTerrenos = driver.find_elements(
                            By.XPATH, "//a[@class='property-card__content-link js-card-title']")
                        for terreno in elementosTerrenos:
                            linksTerrenos.append(terreno.get_attribute('href'))
                    st.success(
                        str(qtdPaginas) + ' página(s) e ' + str(len(linksTerrenos)) + ' anúncio(s) foram encontrados.')

                # Pega o título dos resultados
                tituloResultado = driver.find_element(By.CLASS_NAME, "results-summary__data").text
                sTituloResultado = tituloResultado.split()
                tituloArquivo = sTituloResultado[1] + '_' + sTituloResultado[5] + sTituloResultado[6] + sTituloResultado[7] + '.xlsx'

                # Cria listas de dados
                linksImagensTerrenos = []
                titulosTerrenos = []
                enderecosTerrenos = []
                metragensTerrenos = []
                precosTerrenos = []

                
                barraProgresso = st.progress(0)
                divisorBarraProgresso = int(100 / len(linksTerrenos))
                placeholder = st.empty()
                for i in range(len(linksTerrenos)):
                    driver.get(linksTerrenos[i])
                    time.sleep(5)
                    #try:
                    #    WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    #        (By.XPATH, "//h1[@class='title__title js-title-view']")))
                    #except:
                    #    driver.refresh()
                    imagemLinkTerreno = driver.find_element(
                        By.XPATH, "//div[@class='hero js-hero']//div[@class='carousel js-carousel']//img").get_attribute("src")
                    linksImagensTerrenos.append(imagemLinkTerreno)

                    tituloTerreno = driver.find_element(
                        By.TAG_NAME, "h1").text
                    titulosTerrenos.append(tituloTerreno)

                    enderecoTerreno = driver.find_element(
                        By.XPATH, "//p[@class='title__address js-address']").text
                    enderecosTerrenos.append(enderecoTerreno)

                    metragemTerreno = driver.find_element(
                        By.XPATH, "//li[@class='features__item features__item--area js-area']").text
                    metragensTerrenos.append(metragemTerreno)

                    precoTerreno = driver.find_element(
                        By.XPATH, "//h3[@class='price__price-info js-price-sale']").text
                    precosTerrenos.append(precoTerreno)
                    
                    with placeholder.container():
                        st.write("Coletando dados... Anúncio "+ str(i + 1) + " de " + str(len(linksTerrenos)))  

                    barraProgresso.progress((i + 1)*divisorBarraProgresso)


                st.success("Coleta de dados finalizada com sucesso!")
                driver.quit()
                
                # Cria estrutura de dados
                st.subheader("Tabela gerada:")
                buffer = io.BytesIO()
                tabelaDados = pd.DataFrame(data={'Link Imagem Principal': linksImagensTerrenos,
                                                 'Título anúncio': titulosTerrenos, 'Endereço': enderecosTerrenos, 'Metragem': metragensTerrenos, 'Preço': precosTerrenos})
                st.dataframe(tabelaDados)

                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    tabelaDados.to_excel(writer, sheet_name='Terrenos')

                    writer.save()

                    st.download_button(
                        label="Baixe a tabela aqui!",
                        data=buffer,
                        file_name=tituloArquivo,
                        mime="application/vnd.ms-excel"
                    )
                # add points
                print("--- %s seconds ---" % (time.time() - start_time))
        else:
            st.error('Insira um link correto!')