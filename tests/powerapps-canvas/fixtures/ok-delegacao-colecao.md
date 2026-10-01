Screens:
  Tela Exemplo:
    Properties:
      Fill: =fxColorBackground
      Height: =1080
      Width: =1920
    Children:
      - ex-gal-lista:
          Control: Gallery@2.15.0
          Properties:
            Items: =Filter(colPedidos, "abc" in Descricao)
