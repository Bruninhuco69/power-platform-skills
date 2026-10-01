Screens:
  Tela Exemplo:
    Properties:
      Fill: =fxColorBackground
      Height: =1080
      Width: =1920
      OnVisible: |-
        =Set(varShowLoading, false);
        Set(varShowToast, false)
    Children:
      - ex-lbl-titulo:
          Control: Label@2.5.1
          Properties:
            Text: ="Olá"
      - ex-btn-salvar:
          Control: Classic/Button@2.2.0
          Properties:
            Text: ="Salvar"
            OnSelect: |-
              =Set(varShowLoading, true);
              IfError(
                Set(varRet, 'ex-flow-salvar'.Run("a")),
                Set(varRet, Blank())
              );
              Set(varShowLoading, false)
      - ex-mod-confirmar:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            Visible: =false
      - ex-cmp-loading:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            Visible: =varShowLoading
      - ex-cmp-toast:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            Visible: =varShowToast
