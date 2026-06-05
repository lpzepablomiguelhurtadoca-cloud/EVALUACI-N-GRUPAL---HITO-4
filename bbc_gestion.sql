-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 05-06-2026 a las 21:27:32
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `bbc_gestion`
--

DELIMITER $$
--
-- Procedimientos
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `registrar_movimiento` (IN `p_tipo` ENUM('ENTRADA','SALIDA','TRASLADO'), IN `p_bodega_origen` INT, IN `p_bodega_destino` INT, IN `p_lote_id` INT, IN `p_cantidad` INT, IN `p_usuario` VARCHAR(50), IN `p_observaciones` TEXT)   BEGIN
    DECLARE stock_actual INT;
    
    -- Insertar en historial
    INSERT INTO movimientos (tipo_movimiento, bodega_origen_id, bodega_destino_id, lote_id, cantidad, usuario_responsable, observaciones)
    VALUES (p_tipo, p_bodega_origen, p_bodega_destino, p_lote_id, p_cantidad, p_usuario, p_observaciones);
    
    -- Actualizar stock según tipo
    IF p_tipo = 'ENTRADA' THEN
        INSERT INTO stock (bodega_id, lote_id, cantidad) 
        VALUES (p_bodega_destino, p_lote_id, p_cantidad)
        ON DUPLICATE KEY UPDATE cantidad = cantidad + p_cantidad;
    ELSEIF p_tipo = 'SALIDA' THEN
        UPDATE stock SET cantidad = cantidad - p_cantidad 
        WHERE bodega_id = p_bodega_origen AND lote_id = p_lote_id;
    ELSEIF p_tipo = 'TRASLADO' THEN
        -- Restar del origen
        UPDATE stock SET cantidad = cantidad - p_cantidad 
        WHERE bodega_id = p_bodega_origen AND lote_id = p_lote_id;
        -- Sumar al destino
        INSERT INTO stock (bodega_id, lote_id, cantidad) 
        VALUES (p_bodega_destino, p_lote_id, p_cantidad)
        ON DUPLICATE KEY UPDATE cantidad = cantidad + p_cantidad;
    END IF;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `reporte_rotacion` (IN `p_producto_id` INT)   BEGIN
    SELECT 
        p.nombre_comercial,
        p.presentacion,
        MONTHNAME(m.fecha_movimiento) AS mes,
        SUM(CASE WHEN m.tipo_movimiento = 'SALIDA' THEN m.cantidad ELSE 0 END) AS unidades_vendidas,
        AVG(s.cantidad) AS stock_promedio
    FROM movimientos m
    JOIN lotes l ON m.lote_id = l.id
    JOIN productos p ON l.producto_id = p.id
    LEFT JOIN stock s ON s.lote_id = l.id
    WHERE p.id = p_producto_id
    AND m.fecha_movimiento >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
    GROUP BY YEAR(m.fecha_movimiento), MONTH(m.fecha_movimiento), p.id
    ORDER BY m.fecha_movimiento DESC;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alertas_inventario`
--

CREATE TABLE `alertas_inventario` (
  `id` int(11) NOT NULL,
  `lote_id` int(11) DEFAULT NULL,
  `bodega_id` int(11) DEFAULT NULL,
  `mensaje` text DEFAULT NULL,
  `fecha` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auditoria_stock`
--

CREATE TABLE `auditoria_stock` (
  `id` int(11) NOT NULL,
  `accion` varchar(20) DEFAULT NULL,
  `bodega_id` int(11) DEFAULT NULL,
  `lote_id` int(11) DEFAULT NULL,
  `cantidad_anterior` int(11) DEFAULT NULL,
  `cantidad_nueva` int(11) DEFAULT NULL,
  `usuario` varchar(50) DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bodegas`
--

CREATE TABLE `bodegas` (
  `id` int(11) NOT NULL,
  `planta_id` int(11) NOT NULL,
  `nombre_bodega` varchar(50) NOT NULL,
  `tipo_bodega` enum('Producto Terminado','Insumos','Refrigerado') NOT NULL,
  `ubicacion_fisica` varchar(100) DEFAULT NULL,
  `capacidad_maxima` int(11) DEFAULT NULL,
  `temperatura` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `bodegas`
--

INSERT INTO `bodegas` (`id`, `planta_id`, `nombre_bodega`, `tipo_bodega`, `ubicacion_fisica`, `capacidad_maxima`, `temperatura`) VALUES
(1, 1, 'Bodega Central', 'Producto Terminado', 'Nave A', 50000, 18.00),
(2, 1, 'Almacén Insumos', 'Insumos', 'Nave B', 20000, 20.00),
(3, 1, 'Cámara Fría', 'Refrigerado', 'Nave C', 15000, 4.00),
(4, 2, 'Bodega Central', 'Producto Terminado', 'Nave Principal', 45000, 18.50),
(5, 2, 'Depósito Insumos', 'Insumos', 'Depósito 1', 18000, 21.00),
(6, 2, 'Refrigerado', 'Refrigerado', 'Cámara 2', 12000, 3.50),
(7, 3, 'Bodega Central', 'Producto Terminado', 'Galpón 1', 60000, 19.00),
(8, 3, 'Insumos', 'Insumos', 'Galpón 2', 25000, 22.00),
(9, 3, 'Frigorífico', 'Refrigerado', 'Cámara Sur', 20000, 4.50);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `distribuidores`
--

CREATE TABLE `distribuidores` (
  `id` int(11) NOT NULL,
  `nit` varchar(20) NOT NULL,
  `razon_social` varchar(100) NOT NULL,
  `direccion` varchar(150) DEFAULT NULL,
  `ciudad` varchar(50) DEFAULT NULL,
  `zona` varchar(50) DEFAULT NULL,
  `contacto` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `distribuidores`
--

INSERT INTO `distribuidores` (`id`, `nit`, `razon_social`, `direccion`, `ciudad`, `zona`, `contacto`, `telefono`, `correo`) VALUES
(1, '1012345017', 'Distribuidora Paceña S.R.L.', 'Av. 6 de Agosto #123', 'La Paz', 'Sopocachi', 'Juan Pérez', '76543210', 'ventas@pacena.bo'),
(2, '1023456789', 'Cervezas del Valle Ltda.', 'Calle Bolívar #456', 'Cochabamba', 'Queru Queru', 'María Vargas', '71234567', 'maria@delvalle.com'),
(3, '1034567890', 'Distribuidora Cruceña', 'Av. San Martín #789', 'Santa Cruz', 'Equipetrol', 'José Gutiérrez', '78901234', 'jg@crucenia.bo'),
(4, '1045678901', 'Imperial Beer S.A.', 'Calle Potosí #101', 'La Paz', 'Miraflores', 'Rosa Limachi', '77665544', 'imperial@beer.bo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lotes`
--

CREATE TABLE `lotes` (
  `id` int(11) NOT NULL,
  `numero_lote` varchar(30) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `fecha_produccion` date NOT NULL,
  `fecha_vencimiento` date NOT NULL,
  `cantidad_producida` int(11) NOT NULL,
  `planta_id` int(11) NOT NULL,
  `control_calidad` enum('Aprobado','Rechazado') NOT NULL,
  `tecnico_responsable` varchar(100) DEFAULT NULL,
  `observaciones` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `lotes`
--

INSERT INTO `lotes` (`id`, `numero_lote`, `producto_id`, `fecha_produccion`, `fecha_vencimiento`, `cantidad_producida`, `planta_id`, `control_calidad`, `tecnico_responsable`, `observaciones`) VALUES
(1, 'L20250101', 1, '2025-01-01', '2025-07-01', 5000, 1, 'Aprobado', 'Carlos Mamani', 'Producción normal'),
(2, 'L20250102', 2, '2025-01-05', '2025-07-05', 3000, 1, 'Aprobado', 'Ana Flores', NULL),
(3, 'L20250103', 3, '2025-01-10', '2025-07-10', 4000, 2, 'Rechazado', 'Luis Torrez', 'Problema de etiquetado'),
(4, 'L20250104', 4, '2025-01-12', '2025-07-12', 3500, 2, 'Aprobado', 'María Claure', NULL),
(5, 'L20250105', 5, '2025-01-15', '2025-07-15', 6000, 3, 'Aprobado', 'Juan Carlos', 'Lote premium'),
(6, 'L20250106', 6, '2025-01-18', '2025-07-18', 4500, 3, 'Aprobado', 'Roberto Fernández', NULL),
(7, 'L20250107', 7, '2025-01-20', '2025-07-20', 2000, 1, 'Aprobado', 'Elena Quispe', 'Edición especial'),
(8, 'L20250108', 8, '2025-01-22', '2025-07-22', 1500, 2, 'Aprobado', 'Pedro Rocha', 'Malta sin alcohol');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `movimientos`
--

CREATE TABLE `movimientos` (
  `id` int(11) NOT NULL,
  `tipo_movimiento` enum('ENTRADA','SALIDA','TRASLADO') NOT NULL,
  `bodega_origen_id` int(11) DEFAULT NULL,
  `bodega_destino_id` int(11) DEFAULT NULL,
  `lote_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `fecha_movimiento` datetime DEFAULT current_timestamp(),
  `usuario_responsable` varchar(50) DEFAULT NULL,
  `pedido_id` int(11) DEFAULT NULL,
  `observaciones` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `movimientos`
--

INSERT INTO `movimientos` (`id`, `tipo_movimiento`, `bodega_origen_id`, `bodega_destino_id`, `lote_id`, `cantidad`, `fecha_movimiento`, `usuario_responsable`, `pedido_id`, `observaciones`) VALUES
(1, 'ENTRADA', NULL, 1, 1, 5000, '2026-06-05 15:20:52', 'sistema', NULL, 'Producción enero'),
(2, 'ENTRADA', NULL, 1, 2, 3000, '2026-06-05 15:20:52', 'sistema', NULL, 'Producción enero'),
(3, 'ENTRADA', NULL, 4, 4, 3500, '2026-06-05 15:20:52', 'sistema', NULL, 'Producción Cochabamba'),
(4, 'ENTRADA', NULL, 7, 5, 6000, '2026-06-05 15:20:52', 'sistema', NULL, 'Producción Santa Cruz');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `id` int(11) NOT NULL,
  `distribuidor_id` int(11) NOT NULL,
  `fecha_pedido` date NOT NULL,
  `fecha_entrega_requerida` date DEFAULT NULL,
  `estado` enum('Pendiente','Despachado','Entregado','Cancelado') DEFAULT 'Pendiente',
  `numero_factura` varchar(30) DEFAULT NULL,
  `monto_total` decimal(12,2) DEFAULT NULL,
  `estado_pago` enum('Pagado','Pendiente','Parcial') DEFAULT 'Pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedidos`
--

INSERT INTO `pedidos` (`id`, `distribuidor_id`, `fecha_pedido`, `fecha_entrega_requerida`, `estado`, `numero_factura`, `monto_total`, `estado_pago`) VALUES
(1, 1, '2025-02-01', '2025-02-05', 'Entregado', 'FAC001', 4250.00, 'Pagado'),
(2, 2, '2025-02-03', '2025-02-08', 'Pendiente', 'FAC002', 2700.00, 'Pendiente'),
(3, 3, '2025-02-10', '2025-02-15', 'Despachado', 'FAC003', 5400.00, 'Pagado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos_detalle`
--

CREATE TABLE `pedidos_detalle` (
  `id` int(11) NOT NULL,
  `pedido_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(12,2) GENERATED ALWAYS AS (`cantidad` * `precio_unitario`) STORED
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedidos_detalle`
--

INSERT INTO `pedidos_detalle` (`id`, `pedido_id`, `producto_id`, `cantidad`, `precio_unitario`) VALUES
(1, 1, 1, 500, 8.50),
(2, 2, 3, 300, 9.00),
(3, 3, 5, 600, 8.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `plantas`
--

CREATE TABLE `plantas` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `ciudad` varchar(50) NOT NULL,
  `ubicacion_exacta` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `plantas`
--

INSERT INTO `plantas` (`id`, `nombre`, `ciudad`, `ubicacion_exacta`) VALUES
(1, 'La Paz', 'La Paz', 'Mecapaca'),
(2, 'Cochabamba', 'Cochabamba', 'Sacaba'),
(3, 'Santa Cruz', 'Santa Cruz', 'Palmasola');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id` int(11) NOT NULL,
  `codigo_unico` varchar(20) NOT NULL,
  `nombre_comercial` varchar(50) NOT NULL,
  `tipo` enum('Lager','Pilsener','Malta','Negra') NOT NULL,
  `presentacion` varchar(10) NOT NULL,
  `graduacion_alcoholica` decimal(3,1) NOT NULL,
  `precio_actual` decimal(10,2) NOT NULL,
  `stock_minimo` int(11) DEFAULT 100,
  `stock_maximo` int(11) DEFAULT 10000
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id`, `codigo_unico`, `nombre_comercial`, `tipo`, `presentacion`, `graduacion_alcoholica`, `precio_actual`, `stock_minimo`, `stock_maximo`) VALUES
(1, 'PAC355', 'Paceña', 'Lager', '355ml', 4.5, 8.50, 200, 5000),
(2, 'PAC620', 'Paceña', 'Lager', '620ml', 4.5, 12.00, 150, 4000),
(3, 'TAQ355', 'Taquiña', 'Pilsener', '355ml', 5.0, 9.00, 200, 4500),
(4, 'TAQ620', 'Taquiña', 'Pilsener', '620ml', 5.0, 13.00, 150, 3500),
(5, 'HUA355', 'Huari', 'Lager', '355ml', 4.8, 8.00, 200, 5000),
(6, 'HUA620', 'Huari', 'Lager', '620ml', 4.8, 11.50, 150, 4000),
(7, 'BOC355', 'Bock', 'Negra', '355ml', 5.5, 10.00, 100, 3000),
(8, 'REA355', 'Real', 'Malta', '355ml', 0.5, 7.00, 100, 2000),
(9, 'IMP355', 'Imperial', 'Lager', '355ml', 4.2, 7.50, 200, 5000),
(10, 'POT355', 'Potosina', 'Pilsener', '355ml', 4.7, 8.50, 150, 4000),
(11, 'COP355', 'Copacabana', 'Lager', '355ml', 4.3, 8.00, 200, 4500);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `stock`
--

CREATE TABLE `stock` (
  `id` int(11) NOT NULL,
  `bodega_id` int(11) NOT NULL,
  `lote_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL DEFAULT 0,
  `ultima_actualizacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `stock`
--

INSERT INTO `stock` (`id`, `bodega_id`, `lote_id`, `cantidad`, `ultima_actualizacion`) VALUES
(1, 1, 1, 5000, '2026-06-05 19:20:52'),
(2, 1, 2, 3000, '2026-06-05 19:20:52'),
(3, 4, 3, 0, '2026-06-05 19:20:52'),
(4, 4, 4, 3500, '2026-06-05 19:20:52'),
(5, 7, 5, 6000, '2026-06-05 19:20:52'),
(6, 7, 6, 4500, '2026-06-05 19:20:52'),
(7, 1, 7, 2000, '2026-06-05 19:20:52'),
(8, 4, 8, 1500, '2026-06-05 19:20:52');

--
-- Disparadores `stock`
--
DELIMITER $$
CREATE TRIGGER `after_stock_update` AFTER UPDATE ON `stock` FOR EACH ROW BEGIN
    IF OLD.cantidad != NEW.cantidad THEN
        INSERT INTO auditoria_stock (accion, bodega_id, lote_id, cantidad_anterior, cantidad_nueva, usuario)
        VALUES ('UPDATE', NEW.bodega_id, NEW.lote_id, OLD.cantidad, NEW.cantidad, CURRENT_USER());
    END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `alerta_stock_minimo` AFTER UPDATE ON `stock` FOR EACH ROW BEGIN
    DECLARE minimo INT;
    DECLARE producto_id_var INT;
    
    -- Obtener stock mínimo del producto asociado al lote
    SELECT p.stock_minimo INTO minimo
    FROM lotes l
    JOIN productos p ON l.producto_id = p.id
    WHERE l.id = NEW.lote_id;
    
    IF NEW.cantidad < minimo THEN
        -- Insertar en una tabla de alertas (simulada, se puede crear)
        INSERT INTO alertas_inventario (lote_id, bodega_id, mensaje, fecha)
        VALUES (NEW.lote_id, NEW.bodega_id, CONCAT('Stock por debajo del mínimo: ', NEW.cantidad, ' < ', minimo), NOW());
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_pedidos_pendientes`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_pedidos_pendientes` (
`distribuidor` varchar(100)
,`pedido_numero` int(11)
,`fecha_pedido` date
,`fecha_entrega_requerida` date
,`monto_total` decimal(12,2)
,`estado` enum('Pendiente','Despachado','Entregado','Cancelado')
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_proximos_vencer`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_proximos_vencer` (
`numero_lote` varchar(30)
,`nombre_comercial` varchar(50)
,`presentacion` varchar(10)
,`fecha_vencimiento` date
,`dias_restantes` int(7)
,`stock_disponible` decimal(32,0)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_stock_planta`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_stock_planta` (
`producto` varchar(50)
,`presentacion` varchar(10)
,`planta` varchar(50)
,`stock_total` decimal(32,0)
);

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_pedidos_pendientes`
--
DROP TABLE IF EXISTS `vista_pedidos_pendientes`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_pedidos_pendientes`  AS SELECT `d`.`razon_social` AS `distribuidor`, `p`.`id` AS `pedido_numero`, `p`.`fecha_pedido` AS `fecha_pedido`, `p`.`fecha_entrega_requerida` AS `fecha_entrega_requerida`, `p`.`monto_total` AS `monto_total`, `p`.`estado` AS `estado` FROM (`pedidos` `p` join `distribuidores` `d` on(`p`.`distribuidor_id` = `d`.`id`)) WHERE `p`.`estado` in ('Pendiente','Despachado') ORDER BY `p`.`fecha_entrega_requerida` ASC ;

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_proximos_vencer`
--
DROP TABLE IF EXISTS `vista_proximos_vencer`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_proximos_vencer`  AS SELECT `l`.`numero_lote` AS `numero_lote`, `p`.`nombre_comercial` AS `nombre_comercial`, `p`.`presentacion` AS `presentacion`, `l`.`fecha_vencimiento` AS `fecha_vencimiento`, to_days(`l`.`fecha_vencimiento`) - to_days(curdate()) AS `dias_restantes`, sum(`s`.`cantidad`) AS `stock_disponible` FROM ((`lotes` `l` join `productos` `p` on(`l`.`producto_id` = `p`.`id`)) join `stock` `s` on(`l`.`id` = `s`.`lote_id`)) WHERE `l`.`fecha_vencimiento` between curdate() and curdate() + interval 30 day AND `l`.`control_calidad` = 'Aprobado' GROUP BY `l`.`id` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_stock_planta`
--
DROP TABLE IF EXISTS `vista_stock_planta`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_stock_planta`  AS SELECT `p`.`nombre_comercial` AS `producto`, `p`.`presentacion` AS `presentacion`, `pl`.`nombre` AS `planta`, sum(`s`.`cantidad`) AS `stock_total` FROM ((((`stock` `s` join `lotes` `l` on(`s`.`lote_id` = `l`.`id`)) join `productos` `p` on(`l`.`producto_id` = `p`.`id`)) join `bodegas` `b` on(`s`.`bodega_id` = `b`.`id`)) join `plantas` `pl` on(`b`.`planta_id` = `pl`.`id`)) WHERE `l`.`control_calidad` = 'Aprobado' GROUP BY `p`.`id`, `pl`.`id` ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `alertas_inventario`
--
ALTER TABLE `alertas_inventario`
  ADD PRIMARY KEY (`id`),
  ADD KEY `lote_id` (`lote_id`),
  ADD KEY `bodega_id` (`bodega_id`);

--
-- Indices de la tabla `auditoria_stock`
--
ALTER TABLE `auditoria_stock`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `bodegas`
--
ALTER TABLE `bodegas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_planta_id` (`planta_id`);

--
-- Indices de la tabla `distribuidores`
--
ALTER TABLE `distribuidores`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nit` (`nit`);

--
-- Indices de la tabla `lotes`
--
ALTER TABLE `lotes`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_lote` (`numero_lote`),
  ADD KEY `planta_id` (`planta_id`),
  ADD KEY `idx_fecha_vencimiento` (`fecha_vencimiento`),
  ADD KEY `idx_producto_id` (`producto_id`);

--
-- Indices de la tabla `movimientos`
--
ALTER TABLE `movimientos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `bodega_origen_id` (`bodega_origen_id`),
  ADD KEY `bodega_destino_id` (`bodega_destino_id`),
  ADD KEY `idx_lote_id` (`lote_id`);

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_factura` (`numero_factura`),
  ADD KEY `distribuidor_id` (`distribuidor_id`),
  ADD KEY `idx_fecha_pedido` (`fecha_pedido`);

--
-- Indices de la tabla `pedidos_detalle`
--
ALTER TABLE `pedidos_detalle`
  ADD PRIMARY KEY (`id`),
  ADD KEY `pedido_id` (`pedido_id`),
  ADD KEY `producto_id` (`producto_id`);

--
-- Indices de la tabla `plantas`
--
ALTER TABLE `plantas`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `codigo_unico` (`codigo_unico`);

--
-- Indices de la tabla `stock`
--
ALTER TABLE `stock`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_stock` (`bodega_id`,`lote_id`),
  ADD KEY `idx_stock_lote` (`lote_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `alertas_inventario`
--
ALTER TABLE `alertas_inventario`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auditoria_stock`
--
ALTER TABLE `auditoria_stock`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `bodegas`
--
ALTER TABLE `bodegas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `distribuidores`
--
ALTER TABLE `distribuidores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `lotes`
--
ALTER TABLE `lotes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `movimientos`
--
ALTER TABLE `movimientos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `pedidos_detalle`
--
ALTER TABLE `pedidos_detalle`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `plantas`
--
ALTER TABLE `plantas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `stock`
--
ALTER TABLE `stock`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `alertas_inventario`
--
ALTER TABLE `alertas_inventario`
  ADD CONSTRAINT `alertas_inventario_ibfk_1` FOREIGN KEY (`lote_id`) REFERENCES `lotes` (`id`),
  ADD CONSTRAINT `alertas_inventario_ibfk_2` FOREIGN KEY (`bodega_id`) REFERENCES `bodegas` (`id`);

--
-- Filtros para la tabla `bodegas`
--
ALTER TABLE `bodegas`
  ADD CONSTRAINT `bodegas_ibfk_1` FOREIGN KEY (`planta_id`) REFERENCES `plantas` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `lotes`
--
ALTER TABLE `lotes`
  ADD CONSTRAINT `lotes_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  ADD CONSTRAINT `lotes_ibfk_2` FOREIGN KEY (`planta_id`) REFERENCES `plantas` (`id`);

--
-- Filtros para la tabla `movimientos`
--
ALTER TABLE `movimientos`
  ADD CONSTRAINT `movimientos_ibfk_1` FOREIGN KEY (`bodega_origen_id`) REFERENCES `bodegas` (`id`),
  ADD CONSTRAINT `movimientos_ibfk_2` FOREIGN KEY (`bodega_destino_id`) REFERENCES `bodegas` (`id`),
  ADD CONSTRAINT `movimientos_ibfk_3` FOREIGN KEY (`lote_id`) REFERENCES `lotes` (`id`);

--
-- Filtros para la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`distribuidor_id`) REFERENCES `distribuidores` (`id`);

--
-- Filtros para la tabla `pedidos_detalle`
--
ALTER TABLE `pedidos_detalle`
  ADD CONSTRAINT `pedidos_detalle_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `pedidos_detalle_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`);

--
-- Filtros para la tabla `stock`
--
ALTER TABLE `stock`
  ADD CONSTRAINT `stock_ibfk_1` FOREIGN KEY (`bodega_id`) REFERENCES `bodegas` (`id`),
  ADD CONSTRAINT `stock_ibfk_2` FOREIGN KEY (`lote_id`) REFERENCES `lotes` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
