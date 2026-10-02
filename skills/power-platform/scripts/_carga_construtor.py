"""Pacote do flow Construtor Dataverse (`montar-carga-mockup.py --flow`): a solução não gerenciada (.zip)
para importar e o escopo para colar no designer, os dois montados de `assets/construtor-dataverse.json`.

O flow é o mesmo para todo projeto; quem muda é o plano. O .zip segue o formato de exportação de solução
(`solution.xml`, `customizations.xml`, `Workflows/<nome>-<GUID>.json`) [não verificado: nenhuma importação
deste pacote foi confirmada ainda]. O escopo é o envelope do clipboard do designer novo (a skill
`power-automate`, `references/formato-clipboard.md`): para quando a importação recusar o pacote.
"""
from __future__ import annotations

import io
import json
import uuid
import zipfile
from pathlib import Path
from typing import Any, Callable
from xml.sax.saxutils import escape, quoteattr

ARQ_FLUXO = Path(__file__).resolve().parents[1] / "assets" / "construtor-dataverse.json"
PASTA = "construtor-dataverse"
ZIP = "ConstrutorDataverse_1_0_0_0.zip"
ESCOPO = "construtor-escopo.json"
SOLUCAO, VERSAO = "ConstrutorDataverse", "1.0.0.0"
NOME_FLUXO = "Construtor Dataverse (kit)"
PUBLISHER, PREFIXO, PREFIXO_OPCAO = "kitpowerplatform", "kitpp", 72713
REFERENCIA = f"{PREFIXO}_construtordataversehttp"
API_HTTP = "shared_webcontents"
CONECTOR = f"/providers/Microsoft.PowerApps/apis/{API_HTTP}"
TIPO_REFERENCIA = 10037  # tipo da connection reference no manifesto, o mesmo do pacote do projeto de referência
ID_FLUXO = str(uuid.uuid5(uuid.NAMESPACE_URL, "power-platform-skills/construtor-dataverse"))
DATA_ZIP = (1980, 1, 1, 0, 0, 0)
CAMPOS_ENDERECO = ("City", "County", "Country", "Fax", "FreightTermsCode", "ImportSequenceNumber", "Latitude",
                   "Line1", "Line2", "Line3", "Longitude", "Name", "PostalCode", "PostOfficeBox",
                   "PrimaryContactName")
CAMPOS_ENDERECO_FIM = ("StateOrProvince", "Telephone1", "Telephone2", "Telephone3", "TimeZoneRuleVersionNumber",
                       "UPSZone", "UTCOffset", "UTCConversionTimeZoneCode")


def definicao() -> dict[str, Any]:
    return json.loads(ARQ_FLUXO.read_text(encoding="utf-8"))


def _acoes_http(acoes: dict[str, Any]) -> list[str]:
    """Nome de toda ação de conector, em qualquer nível (If, Scope, Foreach): cada uma precisa da conexão."""
    nomes: list[str] = []
    for nome, acao in acoes.items():
        if acao.get("type") == "OpenApiConnection":
            nomes.append(nome)
        nomes += _acoes_http(acao.get("actions") or {})
        for ramo in (acao.get("else"), acao.get("default"), *(acao.get("cases") or {}).values()):
            nomes += _acoes_http((ramo or {}).get("actions") or {})
    return nomes


def escopo_para_colar(d: dict[str, Any]) -> dict[str, Any]:
    escopo = {**d["actions"]["Construtor"], "runAfter": {}}
    conexao = {"connectionReference": {"api": {"id": CONECTOR}, "connection": {"id": REFERENCIA},
                                       "connectionName": REFERENCIA},
               "referenceKey": API_HTTP}
    return {"nodeId": "Construtor", "serializedValue": escopo,
            "allConnectionData": {nome: conexao for nome in _acoes_http(escopo["actions"])},
            "staticResults": {}, "isScopeNode": True, "mslaNode": True}


def _acao_da_solucao(acao: dict[str, Any]) -> dict[str, Any]:
    if acao.get("type") != "OpenApiConnection":
        return acao
    host = {chave: valor for chave, valor in acao["inputs"]["host"].items() if chave != "connection"}
    return {**acao, "inputs": {**acao["inputs"], "host": {**host, "connectionName": acao["inputs"]["host"]["connection"]},
                               "authentication": "@parameters('$authentication')"}}


def no_formato_da_solucao(acoes: dict[str, Any]) -> dict[str, Any]:
    """O designer escreve `host.connection`; a solução exportada usa `host.connectionName` e `authentication`."""
    saida = {}
    for nome, acao in acoes.items():
        nova = _acao_da_solucao(acao)
        if "actions" in acao:
            nova = {**nova, "actions": no_formato_da_solucao(acao["actions"])}
        for ramo in ("else", "default"):
            if isinstance(acao.get(ramo), dict):
                nova = {**nova, ramo: {**acao[ramo], "actions": no_formato_da_solucao(acao[ramo].get("actions") or {})}}
        if isinstance(acao.get("cases"), dict):
            nova = {**nova, "cases": {caso: {**corpo, "actions": no_formato_da_solucao(corpo.get("actions") or {})}
                                      for caso, corpo in acao["cases"].items()}}
        saida[nome] = nova
    return saida


def _fluxo_da_solucao(d: dict[str, Any]) -> dict[str, Any]:
    referencia = {"runtimeSource": "embedded", "connection": {"connectionReferenceLogicalName": REFERENCIA},
                  "api": {"name": API_HTTP}}
    definicao_da_solucao = {**d, "actions": no_formato_da_solucao(d["actions"])}
    return {"properties": {"connectionReferences": {API_HTTP: referencia}, "definition": definicao_da_solucao},
            "schemaVersion": "1.0.0.0"}


def _endereco(numero: int) -> str:
    nulo = "".join(f"<{campo} xsi:nil=\"true\" />" for campo in CAMPOS_ENDERECO)
    fim = "".join(f"<{campo} xsi:nil=\"true\" />" for campo in CAMPOS_ENDERECO_FIM)
    return (f"<Address><AddressNumber>{numero}</AddressNumber><AddressTypeCode>1</AddressTypeCode>{nulo}"
            f"<ShippingMethodCode>1</ShippingMethodCode>{fim}</Address>")


def solution_xml(idioma: int) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<ImportExportXml version="9.2.24044.191" SolutionPackageVersion="9.2" languagecode="{idioma}" generatedBy="montar-carga-mockup.py" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SolutionManifest>
    <UniqueName>{SOLUCAO}</UniqueName>
    <LocalizedNames><LocalizedName description={quoteattr("Construtor Dataverse")} languagecode="{idioma}" /></LocalizedNames>
    <Descriptions />
    <Version>{VERSAO}</Version>
    <Managed>0</Managed>
    <Publisher>
      <UniqueName>{PUBLISHER}</UniqueName>
      <LocalizedNames><LocalizedName description={quoteattr("Kit Power Platform")} languagecode="{idioma}" /></LocalizedNames>
      <Descriptions />
      <EMailAddress xsi:nil="true" />
      <SupportingWebsiteUrl xsi:nil="true" />
      <CustomizationPrefix>{PREFIXO}</CustomizationPrefix>
      <CustomizationOptionValuePrefix>{PREFIXO_OPCAO}</CustomizationOptionValuePrefix>
      <Addresses>{_endereco(1)}{_endereco(2)}</Addresses>
    </Publisher>
    <RootComponents>
      <RootComponent type="29" id="{{{ID_FLUXO}}}" behavior="0" />
      <RootComponent type="{TIPO_REFERENCIA}" schemaName="{REFERENCIA}" behavior="0" />
    </RootComponents>
    <MissingDependencies />
  </SolutionManifest>
</ImportExportXml>
"""


def customizations_xml(idioma: int, arquivo: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<ImportExportXml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Entities />
  <Roles />
  <Workflows>
    <Workflow WorkflowId="{{{ID_FLUXO}}}" Name={quoteattr(NOME_FLUXO)}>
      <JsonFileName>/{escape(arquivo)}</JsonFileName>
      <Type>1</Type><Subprocess>0</Subprocess><Category>5</Category><Mode>0</Mode>
      <Scope>4</Scope><OnDemand>0</OnDemand><TriggerOnCreate>0</TriggerOnCreate>
      <TriggerOnDelete>0</TriggerOnDelete><AsyncAutodelete>0</AsyncAutodelete>
      <SyncWorkflowLogOnFailure>0</SyncWorkflowLogOnFailure><StateCode>0</StateCode>
      <StatusCode>1</StatusCode><RunAs>1</RunAs><IsTransacted>1</IsTransacted>
      <IntroducedVersion>1.0</IntroducedVersion><IsCustomizable>1</IsCustomizable>
      <BusinessProcessType>0</BusinessProcessType>
      <IsCustomProcessingStepAllowedForOtherPublishers>1</IsCustomProcessingStepAllowedForOtherPublishers>
      <PrimaryEntity>none</PrimaryEntity>
      <LocalizedNames><LocalizedName languagecode="{idioma}" description={quoteattr(NOME_FLUXO)} /></LocalizedNames>
    </Workflow>
  </Workflows>
  <FieldSecurityProfiles />
  <Templates />
  <EntityMaps />
  <EntityRelationships />
  <OrganizationSettings />
  <optionsets />
  <CustomControls />
  <connectionreferences>
    <connectionreference connectionreferencelogicalname="{REFERENCIA}">
      <connectionreferencedisplayname>{escape("Construtor Dataverse - HTTP com Microsoft Entra ID")}</connectionreferencedisplayname>
      <connectorid>{CONECTOR}</connectorid>
      <iscustomizable>1</iscustomizable><statecode>0</statecode><statuscode>1</statuscode>
    </connectionreference>
  </connectionreferences>
  <Languages><Language>{idioma}</Language></Languages>
</ImportExportXml>
"""


CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="text/xml" />
  <Default Extension="json" ContentType="application/json" />
</Types>
"""


def pacote_zip(idioma: int) -> bytes:
    """Zip determinístico: data fixa e ordem fixa, para o mesmo spec dar os mesmos bytes."""
    arquivo = f"Workflows/{SOLUCAO}-{ID_FLUXO.upper()}.json"
    conteudo = {
        "[Content_Types].xml": CONTENT_TYPES,
        "solution.xml": solution_xml(idioma),
        "customizations.xml": customizations_xml(idioma, arquivo),
        arquivo: json.dumps(_fluxo_da_solucao(definicao()), ensure_ascii=False, indent=1),
    }
    saida = io.BytesIO()
    with zipfile.ZipFile(saida, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for nome, texto in conteudo.items():
            info = zipfile.ZipInfo(nome, DATA_ZIP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0  # sem isso, Windows e Linux geram bytes diferentes
            info.external_attr = 0o644 << 16
            z.writestr(info, texto.encode("utf-8"))
    return saida.getvalue()


def escopo_em_bytes() -> bytes:
    return (json.dumps(escopo_para_colar(definicao()), ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def arquivos_do_construtor(idioma: int) -> list[tuple[str, Callable[[], bytes]]]:
    """(caminho relativo à --saida, gerador do conteúdo) de cada arquivo do construtor."""
    return [(f"{PASTA}/{ZIP}", lambda: pacote_zip(idioma)), (f"{PASTA}/{ESCOPO}", escopo_em_bytes)]
