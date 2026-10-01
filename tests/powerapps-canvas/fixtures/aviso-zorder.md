Screens:
  Tela Exemplo:
    Properties:
      Fill: =fxColorBackground
      Height: =1080
      Width: =1920
    Children:
      - ex-cmp-toast:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            Visible: =varShowToast
      - ex-lbl-depois:
          Control: Label@2.5.1
          Properties:
            Text: ="Olá"
