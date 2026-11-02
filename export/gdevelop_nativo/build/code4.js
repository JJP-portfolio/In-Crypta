gdjs.SalasCode = {};
gdjs.SalasCode.localVariables = [];
gdjs.SalasCode.idToCallbackMap = new Map();
gdjs.SalasCode.GDFondoSalasObjects1= [];
gdjs.SalasCode.GDFondoSalasObjects2= [];
gdjs.SalasCode.GDSalas_9595TituloObjects1= [];
gdjs.SalasCode.GDSalas_9595TituloObjects2= [];
gdjs.SalasCode.GDSalas_9595SubObjects1= [];
gdjs.SalasCode.GDSalas_9595SubObjects2= [];
gdjs.SalasCode.GDSalas_9595Opcion1Objects1= [];
gdjs.SalasCode.GDSalas_9595Opcion1Objects2= [];
gdjs.SalasCode.GDSalas_9595Opcion2Objects1= [];
gdjs.SalasCode.GDSalas_9595Opcion2Objects2= [];
gdjs.SalasCode.GDSalas_9595Opcion3Objects1= [];
gdjs.SalasCode.GDSalas_9595Opcion3Objects2= [];
gdjs.SalasCode.GDSalas_9595Opcion4Objects1= [];
gdjs.SalasCode.GDSalas_9595Opcion4Objects2= [];
gdjs.SalasCode.GDSalas_9595Opcion5Objects1= [];
gdjs.SalasCode.GDSalas_9595Opcion5Objects2= [];
gdjs.SalasCode.GDSalas_9595Opcion6Objects1= [];
gdjs.SalasCode.GDSalas_9595Opcion6Objects2= [];
gdjs.SalasCode.GDSalas_9595Desc1Objects1= [];
gdjs.SalasCode.GDSalas_9595Desc1Objects2= [];
gdjs.SalasCode.GDSalas_9595Desc2Objects1= [];
gdjs.SalasCode.GDSalas_9595Desc2Objects2= [];
gdjs.SalasCode.GDSalas_9595AyudaObjects1= [];
gdjs.SalasCode.GDSalas_9595AyudaObjects2= [];


gdjs.SalasCode.eventsList0 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.runtimeScene.sceneJustBegins(runtimeScene);
if (isConditionTrue_0) {
{runtimeScene.getScene().getVariables().getFromIndex(0).setNumber(1);
}
{runtimeScene.getGame().getVariables().getFromIndex(11).setNumber(512);
}
{runtimeScene.getGame().getVariables().getFromIndex(12).setNumber(288);
}
{runtimeScene.getGame().getVariables().getFromIndex(13).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(14).setNumber(0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 1.25, "", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 512, "", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 288, "", 0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 1, "UI", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 640, "UI", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 360, "UI", 0);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 1);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc1"), gdjs.SalasCode.GDSalas_9595Desc1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc2"), gdjs.SalasCode.GDSalas_9595Desc2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion1"), gdjs.SalasCode.GDSalas_9595Opcion1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion2"), gdjs.SalasCode.GDSalas_9595Opcion2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion3"), gdjs.SalasCode.GDSalas_9595Opcion3Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion4"), gdjs.SalasCode.GDSalas_9595Opcion4Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion5"), gdjs.SalasCode.GDSalas_9595Opcion5Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion6"), gdjs.SalasCode.GDSalas_9595Opcion6Objects1);
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion1Objects1[i].setString(">> 1 · SALA 1 · MOVIMIENTO <<");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion2Objects1[i].setString("2 · SALA 2 · PALA Y ATAQUE");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion3Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion3Objects1[i].setString("3 · SALA 3 · CUSTODIO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion4Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion4Objects1[i].setString("4 · SALA 1 REDISEÑADA · SALTO + DASH");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion5Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion5Objects1[i].setString("5 · SALA 2 REDISEÑADA · ARMA + PISOTÓN Y DASH");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion6Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion6Objects1[i].setString("6 · SALA 3 REDISEÑADA · MINI-BOSS + GUADAÑA + CUSTODIO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc1Objects1[i].setString("NIVEL 1: 4 beats de la Sierra. (1) Saltos 3-4 tiles y esquiva morador, (2) Altar Dash");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc2Objects1[i].setString("y trinchera segura, (3) Farol 1 y fosos de Dash, (4) Farol 2 y secuencia rítmica hasta");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 2);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc1"), gdjs.SalasCode.GDSalas_9595Desc1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc2"), gdjs.SalasCode.GDSalas_9595Desc2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion1"), gdjs.SalasCode.GDSalas_9595Opcion1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion2"), gdjs.SalasCode.GDSalas_9595Opcion2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion3"), gdjs.SalasCode.GDSalas_9595Opcion3Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion4"), gdjs.SalasCode.GDSalas_9595Opcion4Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion5"), gdjs.SalasCode.GDSalas_9595Opcion5Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion6"), gdjs.SalasCode.GDSalas_9595Opcion6Objects1);
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion1Objects1[i].setString("1 · SALA 1 · MOVIMIENTO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion2Objects1[i].setString(">> 2 · SALA 2 · PALA Y ATAQUE <<");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion3Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion3Objects1[i].setString("3 · SALA 3 · CUSTODIO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion4Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion4Objects1[i].setString("4 · SALA 1 REDISEÑADA · SALTO + DASH");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion5Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion5Objects1[i].setString("5 · SALA 2 REDISEÑADA · ARMA + PISOTÓN Y DASH");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion6Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion6Objects1[i].setString("6 · SALA 3 REDISEÑADA · MINI-BOSS + GUADAÑA + CUSTODIO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc1Objects1[i].setString("SALA 2: recogé la pala. Probá el ataque con J o clic; un pisotón exitoso recarga el dash.");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc2Objects1[i].setString("En el aire, encadená Dash + pisotón + segundo Dash.");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 3);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc1"), gdjs.SalasCode.GDSalas_9595Desc1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc2"), gdjs.SalasCode.GDSalas_9595Desc2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion1"), gdjs.SalasCode.GDSalas_9595Opcion1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion2"), gdjs.SalasCode.GDSalas_9595Opcion2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion3"), gdjs.SalasCode.GDSalas_9595Opcion3Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion4"), gdjs.SalasCode.GDSalas_9595Opcion4Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion5"), gdjs.SalasCode.GDSalas_9595Opcion5Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion6"), gdjs.SalasCode.GDSalas_9595Opcion6Objects1);
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion1Objects1[i].setString("1 · SALA 1 · MOVIMIENTO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion2Objects1[i].setString("2 · SALA 2 · PALA Y ATAQUE");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion3Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion3Objects1[i].setString(">> 3 · SALA 3 · CUSTODIO <<");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion4Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion4Objects1[i].setString("4 · SALA 1 REDISEÑADA · SALTO + DASH");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion5Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion5Objects1[i].setString("5 · SALA 2 REDISEÑADA · ARMA + PISOTÓN Y DASH");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion6Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion6Objects1[i].setString("6 · SALA 3 REDISEÑADA · MINI-BOSS + GUADAÑA + CUSTODIO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc1Objects1[i].setString("TEST ROOM 3: tenés la pala. Saltá las ondas del Custodio y golpealo cuando se");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc2Objects1[i].setString("arrodilla. La salida se abre al vencerlo.");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 4);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc1"), gdjs.SalasCode.GDSalas_9595Desc1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc2"), gdjs.SalasCode.GDSalas_9595Desc2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion1"), gdjs.SalasCode.GDSalas_9595Opcion1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion2"), gdjs.SalasCode.GDSalas_9595Opcion2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion3"), gdjs.SalasCode.GDSalas_9595Opcion3Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion4"), gdjs.SalasCode.GDSalas_9595Opcion4Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion5"), gdjs.SalasCode.GDSalas_9595Opcion5Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion6"), gdjs.SalasCode.GDSalas_9595Opcion6Objects1);
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion1Objects1[i].setString("1 · SALA 1 · MOVIMIENTO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion2Objects1[i].setString("2 · SALA 2 · PALA Y ATAQUE");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion3Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion3Objects1[i].setString("3 · SALA 3 · CUSTODIO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion4Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion4Objects1[i].setString(">> 4 · SALA 1 REDISEÑADA · SALTO + DASH <<");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion5Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion5Objects1[i].setString("5 · SALA 2 REDISEÑADA · ARMA + PISOTÓN Y DASH");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion6Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion6Objects1[i].setString("6 · SALA 3 REDISEÑADA · MINI-BOSS + GUADAÑA + CUSTODIO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc1Objects1[i].setString("SALA 1: Salto variable y Dash. Fosos con trinchera segura para practicar.");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc2Objects1[i].setString("");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 5);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc1"), gdjs.SalasCode.GDSalas_9595Desc1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc2"), gdjs.SalasCode.GDSalas_9595Desc2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion1"), gdjs.SalasCode.GDSalas_9595Opcion1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion2"), gdjs.SalasCode.GDSalas_9595Opcion2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion3"), gdjs.SalasCode.GDSalas_9595Opcion3Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion4"), gdjs.SalasCode.GDSalas_9595Opcion4Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion5"), gdjs.SalasCode.GDSalas_9595Opcion5Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion6"), gdjs.SalasCode.GDSalas_9595Opcion6Objects1);
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion1Objects1[i].setString("1 · SALA 1 · MOVIMIENTO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion2Objects1[i].setString("2 · SALA 2 · PALA Y ATAQUE");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion3Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion3Objects1[i].setString("3 · SALA 3 · CUSTODIO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion4Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion4Objects1[i].setString("4 · SALA 1 REDISEÑADA · SALTO + DASH");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion5Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion5Objects1[i].setString(">> 5 · SALA 2 REDISEÑADA · ARMA + PISOTÓN Y DASH <<");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion6Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion6Objects1[i].setString("6 · SALA 3 REDISEÑADA · MINI-BOSS + GUADAÑA + CUSTODIO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc1Objects1[i].setString("SALA 2: Recogé la pala en el altar. Usá J o clic para atacar y practicá el pisotón que recarga el Dash.");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc2Objects1[i].setString("recargar el Dash.");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 6);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc1"), gdjs.SalasCode.GDSalas_9595Desc1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Desc2"), gdjs.SalasCode.GDSalas_9595Desc2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion1"), gdjs.SalasCode.GDSalas_9595Opcion1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion2"), gdjs.SalasCode.GDSalas_9595Opcion2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion3"), gdjs.SalasCode.GDSalas_9595Opcion3Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion4"), gdjs.SalasCode.GDSalas_9595Opcion4Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion5"), gdjs.SalasCode.GDSalas_9595Opcion5Objects1);
gdjs.copyArray(runtimeScene.getObjects("Salas_Opcion6"), gdjs.SalasCode.GDSalas_9595Opcion6Objects1);
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion1Objects1[i].setString("1 · SALA 1 · MOVIMIENTO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion2Objects1[i].setString("2 · SALA 2 · PALA Y ATAQUE");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion3Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion3Objects1[i].setString("3 · SALA 3 · CUSTODIO");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion4Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion4Objects1[i].setString("4 · SALA 1 REDISEÑADA · SALTO + DASH");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion5Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion5Objects1[i].setString("5 · SALA 2 REDISEÑADA · ARMA + PISOTÓN Y DASH");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Opcion6Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Opcion6Objects1[i].setString(">> 6 · SALA 3 REDISEÑADA · MINI-BOSS + GUADAÑA + CUSTODIO <<");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc1Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc1Objects1[i].setString("SALA 3: Vencí al Carcelero y tomá la Guadaña Consagrada; luego preparate para el Custodio.");
}
}
{for(var i = 0, len = gdjs.SalasCode.GDSalas_9595Desc2Objects1.length ;i < len;++i) {
    gdjs.SalasCode.GDSalas_9595Desc2Objects1[i].setString("");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Up");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "w");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 1);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).setNumber(6);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Up");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "w");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() > 1);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).sub(1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Down");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "s");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 6);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).setNumber(1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Down");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "s");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() < 6);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).add(1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 1);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 1", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 2);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 2", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 3);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 3", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 4);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 4", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 5);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 5", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 6);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 6", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "1");
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 1", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "2");
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 2", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "3");
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 3", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "4");
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 4", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "5");
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 5", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "6");
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Sala 6", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Escape");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "t");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Titulo", false);
}
}

}


};

gdjs.SalasCode.func = function(runtimeScene) {
runtimeScene.getOnceTriggers().startNewFrame();

gdjs.SalasCode.GDFondoSalasObjects1.length = 0;
gdjs.SalasCode.GDFondoSalasObjects2.length = 0;
gdjs.SalasCode.GDSalas_9595TituloObjects1.length = 0;
gdjs.SalasCode.GDSalas_9595TituloObjects2.length = 0;
gdjs.SalasCode.GDSalas_9595SubObjects1.length = 0;
gdjs.SalasCode.GDSalas_9595SubObjects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion1Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion1Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion2Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion2Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion3Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion3Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion4Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion4Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion5Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion5Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion6Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion6Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Desc1Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Desc1Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Desc2Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Desc2Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595AyudaObjects1.length = 0;
gdjs.SalasCode.GDSalas_9595AyudaObjects2.length = 0;

gdjs.SalasCode.eventsList0(runtimeScene);
gdjs.SalasCode.GDFondoSalasObjects1.length = 0;
gdjs.SalasCode.GDFondoSalasObjects2.length = 0;
gdjs.SalasCode.GDSalas_9595TituloObjects1.length = 0;
gdjs.SalasCode.GDSalas_9595TituloObjects2.length = 0;
gdjs.SalasCode.GDSalas_9595SubObjects1.length = 0;
gdjs.SalasCode.GDSalas_9595SubObjects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion1Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion1Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion2Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion2Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion3Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion3Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion4Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion4Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion5Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion5Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion6Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Opcion6Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Desc1Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Desc1Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595Desc2Objects1.length = 0;
gdjs.SalasCode.GDSalas_9595Desc2Objects2.length = 0;
gdjs.SalasCode.GDSalas_9595AyudaObjects1.length = 0;
gdjs.SalasCode.GDSalas_9595AyudaObjects2.length = 0;


return;

}

gdjs['SalasCode'] = gdjs.SalasCode;
