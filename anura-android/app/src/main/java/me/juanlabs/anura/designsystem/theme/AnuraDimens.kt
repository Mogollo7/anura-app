package me.juanlabs.anura.designsystem.theme

import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * Tokens de forma y espaciado de `anura-primitivos` (§3.6). Referenciar siempre estos
 * valores en lugar de números sueltos en composables.
 */
object AnuraDimens {
    /** Radio de esquina de botones. */
    val radiusButton: Dp = 12.dp

    /** Radio de esquina de miniaturas. */
    val radiusThumb: Dp = 12.dp

    /** Radio de esquina de diálogos y radio superior de bottom sheets genéricos. */
    val radiusModal: Dp = 20.dp

    /** Radio de esquina de [me.juanlabs.anura.designsystem.theme.AnuraShapes] — tarjetas. */
    val radiusCard: Dp = 16.dp

    /** Radio superior del sheet de bienvenida / pop-ups de pantalla (LOGIN OR SINGUO). */
    val radiusSheet: Dp = 30.dp

    /** Alto de botones de acción de pantallas (Iniciar sesión / Crear cuenta). */
    val sizeActionButton: Dp = 56.dp

    /** Radio de cápsula para chips (efectivamente circular a la altura usada). */
    val radiusCapsule: Dp = 999.dp

    /** Margen horizontal estándar de pantalla. */
    val spaceGutter: Dp = 20.dp

    /** Espaciado entre elementos relacionados dentro de un mismo grupo. */
    val spaceGap: Dp = 12.dp

    /** Espaciado entre secciones. */
    val spaceSection: Dp = 24.dp

    /**
     * Hueco entre la barra superior y el primer contenido
     * (Penpot `ajustes`: cabecera de perfil ~y=100).
     */
    val spaceTopBarToContent: Dp = 24.dp

    /** Tamaño del FAB central de la navbar (tamaño real del diseño). */
    val sizeFab: Dp = 80.dp

    /**
     * Tamaño táctil mínimo. El token de Penpot/HIG es 44dp; Material 3 exige 48dp
     * y gana por la regla de plataforma (§3.7-P1). Nunca usar 44dp en Android.
     */
    val sizeTouch: Dp = 48.dp

    /**
     * Inset horizontal de botones en pop-ups/sheets de auth
     * (`LOGIN OR SINGUO` / ¿Qué querés registrar?).
     */
    val spacePopupInset: Dp = 56.dp

    /** Gap entre botones de acción apilados o en fila (pop-ups, wizard, auth). */
    val spaceActionGap: Dp = 10.dp

    /** Título → cuerpo en sheets de bienvenida / "¿Qué querés registrar?". */
    val spaceSheetTitleToBody: Dp = 20.dp

    /** Cuerpo → botones en esos sheets. */
    val spaceSheetBodyToActions: Dp = 32.dp

    /** Título de pantalla → subtítulo (wizard y auth). */
    val spaceTitleToSubtitle: Dp = 4.dp

    /** Etiqueta de sección → control/campo que rotula. */
    val spaceLabelToContent: Dp = 8.dp

    /** Relleno interno horizontal de tarjetas de contenido. */
    val spaceCardInsetHorizontal: Dp = 20.dp

    /** Relleno interno vertical de tarjetas de contenido. */
    val spaceCardInsetVertical: Dp = 16.dp
}
