import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15

Rectangle {
    id: root
    color: "#f5f5f5"

    // Definição de sinais - conectados aos callbacks Python
    signal manualButtonPressed()
    signal manualButtonReleased()
    signal autoButtonClicked()
    signal abortButtonClicked()
    signal modeButtonClicked()
    signal sendButtonClicked(string text)
    signal settingsButtonClicked()
    // Sinais da barra de título
    signal titleMinimize()
    signal titleClose()
    signal titleDragStart(real mouseX, real mouseY)
    signal titleDragMoveTo(real mouseX, real mouseY)
    signal titleDragEnd()

    // Layout principal
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 0
        spacing: 0

        // Barra de título personalizada: minimizar, fechar, arrastar
        Rectangle {
            id: titleBar
            Layout.fillWidth: true
            Layout.preferredHeight: 36
            color: "#f7f8fa"
            border.width: 0

            // Arrastar a barra inteira (usa coordenadas da tela para evitar trepidações)
            // Mantida na camada inferior para que os botões recebam o clique primeiro
            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.LeftButton
                onPressed: {
                    root.titleDragStart(mouse.x, mouse.y)
                }
                onPositionChanged: {
                    if (pressed) {
                        root.titleDragMoveTo(mouse.x, mouse.y)
                    }
                }
                onReleased: {
                    root.titleDragEnd()
                }
                z: 0  // Camada inferior
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 8
                spacing: 8
                z: 1  // Camada dos botões acima da área de arrasto

                // Área de arrasto à esquerda
                Item { id: dragArea; Layout.fillWidth: true; Layout.fillHeight: true }

                // Minimizar
                Rectangle {
                    id: btnMin
                    width: 24; height: 24; radius: 6
                    color: btnMinMouse.pressed ? "#e5e6eb" : (btnMinMouse.containsMouse ? "#f2f3f5" : "transparent")
                    z: 2  // Garantir que o botão fique na camada superior
                    Text { anchors.centerIn: parent; text: "–"; font.pixelSize: 14; color: "#4e5969" }
                    MouseArea {
                        id: btnMinMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: root.titleMinimize()
                    }
                }

                // Fechar
                Rectangle {
                    id: btnClose
                    width: 24; height: 24; radius: 6
                    color: btnCloseMouse.pressed ? "#f53f3f" : (btnCloseMouse.containsMouse ? "#ff7875" : "transparent")
                    z: 2  // Garantir que o botão fique na camada superior
                    Text { anchors.centerIn: parent; text: "×"; font.pixelSize: 14; color: btnCloseMouse.containsMouse ? "white" : "#86909c" }
                    MouseArea {
                        id: btnCloseMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: root.titleClose()
                    }
                }
            }
        }

        // Área do cartão de status
        Rectangle {
            id: statusCard
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                // Rótulo de status
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40
                    color: "#E3F2FD"
                    radius: 10

                    Text {
                        anchors.centerIn: parent
                        text: displayModel ? displayModel.statusText : "Estado: Não conectado"
                        font.family: "Segoe UI"
                        font.pixelSize: 14
                        font.weight: Font.Bold
                        color: "#2196F3"
                    }
                }

                // Área de exibição do emoji/figura
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumHeight: 80

                    // Carrega dinamicamente a expressão: AnimatedImage para GIF, Image para imagem estática, Text para emoji
                    Loader {
                        id: emotionLoader
                        anchors.centerIn: parent
                        // Mantém um quadrado com 70% do menor entre largura/altura (mínimo 60px)
                        property real maxSize: Math.max(Math.min(parent.width, parent.height) * 0.7, 60)
                        width: maxSize
                        height: maxSize

                        sourceComponent: {
                            var path = displayModel ? displayModel.emotionPath : ""
                            if (!path || path.length === 0) {
                                return emojiComponent
                            }
                            if (path.indexOf(".gif") !== -1) {
                                return gifComponent
                            }
                            if (path.indexOf(".") !== -1) {
                                return imageComponent
                            }
                            return emojiComponent
                        }

                        // Componente para GIF
                        Component {
                            id: gifComponent
                            AnimatedImage {
                                fillMode: Image.PreserveAspectCrop
                                source: displayModel ? displayModel.emotionPath : ""
                                playing: true
                                speed: 1.05
                                cache: true
                                clip: true
                                onStatusChanged: {
                                    if (status === Image.Error) {
                                        console.error("AnimatedImage error:", errorString, "src=", source)
                                    }
                                }
                            }
                        }

                        // Componente para imagem estática
                        Component {
                            id: imageComponent
                            Image {
                                fillMode: Image.PreserveAspectCrop
                                source: displayModel ? displayModel.emotionPath : ""
                                cache: true
                                clip: true
                                onStatusChanged: {
                                    if (status === Image.Error) {
                                        console.error("Image error:", errorString, "src=", source)
                                    }
                                }
                            }
                        }

                        // Componente para emoji (texto)
                        Component {
                            id: emojiComponent
                            Text {
                                text: displayModel ? displayModel.emotionPath : "😊"
                                font.pixelSize: 80
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }

                // Área de exibição do TTS
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    color: "transparent"

                    Text {
                        anchors.fill: parent
                        anchors.margins: 10
                        text: displayModel ? displayModel.ttsText : "Aguardando"
                        font.family: "Segoe UI"
                        font.pixelSize: 13
                        color: "#555555"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }

        // Área dos botões (cores e tamanhos uniformes)
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 72
            color: "#f7f8fa"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                anchors.bottomMargin: 10
                spacing: 6

                // Botão modo manual (pressione para falar) - cor primária
                Button {
                    id: manualBtn
                    Layout.preferredWidth: 100
                    Layout.fillWidth: true
                    Layout.maximumWidth: 140
                    Layout.preferredHeight: 38
                    text: "Pressione para falar"
                    visible: displayModel ? !displayModel.autoMode : true

                    background: Rectangle {
                        color: manualBtn.pressed ? "#0e42d2" : (manualBtn.hovered ? "#4080ff" : "#165dff")
                        radius: 8

                        Behavior on color { ColorAnimation { duration: 120; easing.type: Easing.OutCubic } }
                    }

                    contentItem: Text {
                        text: manualBtn.text
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }

                    onPressed: { manualBtn.text = "Solte para parar"; root.manualButtonPressed() }
                    onReleased: { manualBtn.text = "Pressione para falar"; root.manualButtonReleased() }
                }

                // Botão modo automático - cor primária
                Button {
                    id: autoBtn
                    Layout.preferredWidth: 100
                    Layout.fillWidth: true
                    Layout.maximumWidth: 140
                    Layout.preferredHeight: 38
                    text: (displayModel && displayModel.buttonText && displayModel.buttonText.length > 0) ? displayModel.buttonText : "Iniciar conversa"
                    visible: displayModel ? displayModel.autoMode : false

                    background: Rectangle {
                        color: autoBtn.pressed ? "#0e42d2" : (autoBtn.hovered ? "#4080ff" : "#165dff")
                        radius: 8
                        Behavior on color { ColorAnimation { duration: 120; easing.type: Easing.OutCubic } }
                    }

                    contentItem: Text {
                        text: autoBtn.text
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                    onClicked: root.autoButtonClicked()
                }

                // Interromper conversa - cor secundária
                Button {
                    id: abortBtn
                    Layout.preferredWidth: 80
                    Layout.fillWidth: true
                    Layout.maximumWidth: 120
                    Layout.preferredHeight: 38
                    text: "Interromper"

                    background: Rectangle { color: abortBtn.pressed ? "#e5e6eb" : (abortBtn.hovered ? "#f2f3f5" : "#eceff3"); radius: 8 }
                    contentItem: Text {
                        text: abortBtn.text
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        color: "#1d2129"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                    onClicked: root.abortButtonClicked()
                }

                // Entrada + enviar
                RowLayout {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 120
                    Layout.preferredHeight: 38
                    spacing: 6

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 38
                        color: "white"
                        radius: 8
                        border.color: textInput.activeFocus ? "#165dff" : "#e5e6eb"
                        border.width: 1

                        TextInput {
                            id: textInput
                            anchors.fill: parent
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10
                            verticalAlignment: TextInput.AlignVCenter
                            font.family: "Segoe UI"
                            font.pixelSize: 12
                            color: "#333333"
                            selectByMouse: true
                            clip: true

                            // Placeholder
                            Text { anchors.fill: parent; text: "Digite aqui..."; font: textInput.font; color: "#c9cdd4"; verticalAlignment: Text.AlignVCenter; visible: !textInput.text && !textInput.activeFocus }

                            Keys.onReturnPressed: { if (textInput.text.trim().length > 0) { root.sendButtonClicked(textInput.text); textInput.text = "" } }
                        }
                    }

                    Button {
                        id: sendBtn
                        Layout.preferredWidth: 60
                        Layout.maximumWidth: 84
                        Layout.preferredHeight: 38
                        text: "Enviar"
                        background: Rectangle { color: sendBtn.pressed ? "#0e42d2" : (sendBtn.hovered ? "#4080ff" : "#165dff"); radius: 8 }
                        contentItem: Text {
                            text: sendBtn.text
                            font.family: "Segoe UI"
                            font.pixelSize: 12
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        onClicked: { if (textInput.text.trim().length > 0) { root.sendButtonClicked(textInput.text); textInput.text = "" } }
                    }
                }

                // Modo (secundário)
                Button {
                    id: modeBtn
                    Layout.preferredWidth: 80
                    Layout.fillWidth: true
                    Layout.maximumWidth: 120
                    Layout.preferredHeight: 38
                    text: (displayModel && displayModel.modeText && displayModel.modeText.length > 0) ? displayModel.modeText : "Modo manual"
                    background: Rectangle { color: modeBtn.pressed ? "#e5e6eb" : (modeBtn.hovered ? "#f2f3f5" : "#eceff3"); radius: 8 }
                    contentItem: Text {
                        text: modeBtn.text
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        color: "#1d2129"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                    onClicked: root.modeButtonClicked()
                }

                // Configurações (secundário)
                Button {
                    id: settingsBtn
                    Layout.preferredWidth: 100
                    Layout.fillWidth: true
                    Layout.maximumWidth: 150
                    Layout.preferredHeight: 38
                    text: "Configurações"
                    
                    background: Rectangle { 
                        color: settingsBtn.pressed ? "#e5e6eb" : (settingsBtn.hovered ? "#f2f3f5" : "#eceff3")
                        radius: 8 
                    }
                    contentItem: Text {
                        text: settingsBtn.text
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        font.weight: Font.Medium
                        color: "#1d2129"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideNone
                    }
                    onClicked: root.settingsButtonClicked()
                }
            }
        }
    }
}
