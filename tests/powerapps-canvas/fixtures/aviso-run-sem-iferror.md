Screens:
  Tela Exemplo:
    Properties:
      Fill: =fxColorBackground
      Height: =1080
      Width: =1920
    Children:
      - ex-btn-x:
          Control: Classic/Button@2.2.0
          Properties:
            OnSelect: =Set(varRet, 'ex-flow-salvar'.Run("a"))
