# Tacho de basura — de donde salen las ratas (2026-10-03)

Equivalente al casillero del juego de referencia. Alcance: modelo + animacion de apertura. Fuera: barra Ready, prompt Open, viaje por la cinta, ratas tirando queso.

## Modelo — `ReplicatedStorage.RatRoll.Items.Tacho`
- Tacho de metal chunky (~7 ancho x ~9.7 alto), Plastic + MaterialVariant "Studs", sin Neon ni luces.
- Root invisible (PrimaryPart) en el centro de la base, frente = LookVector (-Z).
- Tacho simple: sin logo ni banda de color en el cuerpo (a pedido); solo la tapa lleva el color de la rareza.
- Escala: template a 0.75; las ratas salen a 1.5x su escala de modelo (lo aplica quien llama, ej. TachoDemoClient).
- Grupos: `Can` (cuerpo, costillas, borde, asas, abolladuras, baba verde, ruedas), `Lid` (tapa + domo + manija), `Eyes` (ojos amarillos dentro de la ranura), `Trash` (espina de pescado, cascara de banana, lata asomando).
- Partes con atributo `Tint` se pintan del color de la rareza.
- Atributos del Root: `RimY`, `Radius` (sin escalar).

## Animacion — `ReplicatedStorage.RatRoll.TachoFX` (cliente)
- `Paint(tacho, rarity)`, `Prepare(tacho, rat, landCF) -> state`, `Pose(state, t)` (pura, sirve para cuadrar fotogramas en Studio), `Finish(state)`, `Play(tacho, rat, landCF, rarity?)` (Heartbeat, sin sonidos: se sacaron a pedido).
- Timeline (~2.8s): 0-0.85 tiembla + 3 saltitos, la tapa traquetea y asoman ojos | 0.8-0.92 se aplasta | 0.92 la tapa sale volando girando, la basura explota en arcos, polvo | 0.95-1.55 la rata sale estirada, voltereta, aterriza en landCF con aplaston | tapa cae ~1.9 y gira como moneda | 1.9-2.45 el tacho se aplasta, se achica girando y desaparece con puf | basura y tapa se achican 2.3-2.8.
- Slot (como la referencia, donde el personaje vuelve al pedestal): `Play(..., slotCF)`. El tacho va arriba del slot (RatPad) mirando a la cinta; la rata aterriza sobre la cinta (landCF, 9 studs adelante), el tacho desaparece y a los 2.55s se agacha y hace un mortal para atras hasta slotCF (mismo frente que el tacho, mirando a la cinta), aterriza con aplaston + polvo. Dura 3.52s. Al final rat.WorldPivot = slotCF.
- Basura, tapa y aterrizaje de la rata buscan el piso real con raycast (el tacho puede estar arriba de un pedestal).
- Deformacion no uniforme (squash/stretch) por parte, tambien para la rata (cache de offsets relativo a su marco de pie).
- La rata entra sin tag RatIdle; quien llama la etiqueta al terminar.

## Prueba
Tacho + BaseRat en la parcela, capturas en t = 0.4 / 0.95 / 1.2 / 1.5 / 2.2, despues playtest con Play().
