Screens:
  Tela Exemplo:
    Properties:
      Fill: =fxColorBackground
      Height: =1080
      Width: =1920
    Children:
      - ex-lbl-titulo:
          Control: =If(true, "Label", "Button")
          Properties:
            Text: ="Olá"
