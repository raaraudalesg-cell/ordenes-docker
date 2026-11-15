SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

IF DB_ID('OrdenesDB') IS NULL
BEGIN
    CREATE DATABASE OrdenesDB;
END;
GO

USE OrdenesDB;
GO

IF OBJECT_ID('dbo.ordenes', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.ordenes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        cliente NVARCHAR(150) NOT NULL,
        fecha DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        estado NVARCHAR(20) NOT NULL DEFAULT 'Pendiente',
        total DECIMAL(12,2) NOT NULL DEFAULT 0,
        CONSTRAINT CK_ordenes_estado
            CHECK (estado IN ('Pendiente', 'Pagada', 'Anulada'))
    );
END;
GO

IF OBJECT_ID('dbo.orden_detalle', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.orden_detalle (
        id INT IDENTITY(1,1) PRIMARY KEY,
        orden_id INT NOT NULL,
        producto NVARCHAR(150) NOT NULL,
        cantidad INT NOT NULL,
        precio_unitario DECIMAL(12,2) NOT NULL,
        subtotal DECIMAL(12,2) NOT NULL,
        CONSTRAINT FK_detalle_orden
            FOREIGN KEY (orden_id)
            REFERENCES dbo.ordenes(id),
        CONSTRAINT CK_detalle_cantidad
            CHECK (cantidad > 0),
        CONSTRAINT CK_detalle_precio
            CHECK (precio_unitario >= 0),
        CONSTRAINT CK_detalle_subtotal
            CHECK (subtotal = cantidad * precio_unitario)
    );
END;
GO

DECLARE @datos TABLE (
    numero INT PRIMARY KEY,
    cliente NVARCHAR(150),
    estado NVARCHAR(20)
);

INSERT INTO @datos (numero, cliente, estado)
VALUES
(1, 'GUSTAVO ADOLFO SIU MARQUEZ', 'Pendiente'),
(2, 'JOSE ALFREDO MEJIA GRANADOS', 'Pagada'),
(3, 'NELSON JAVIER GUERRA NOLASCO', 'Pendiente'),
(4, 'RAUL ANDRES RAUDALES GARCIA', 'Pagada'),
(5, 'RUT NOHEMY SANCHEZ GARCIA', 'Pendiente'),
(6, 'STANLEY LEMUEL GOFF STERBROOCK', 'Anulada');

INSERT INTO dbo.ordenes (cliente, estado)
SELECT d.cliente, d.estado
FROM @datos d
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.ordenes o
    WHERE o.cliente = d.cliente
);

DECLARE @productos TABLE (
    cliente NVARCHAR(150),
    producto NVARCHAR(150),
    cantidad INT,
    precio DECIMAL(12,2)
);

INSERT INTO @productos
(cliente, producto, cantidad, precio)
VALUES
('GUSTAVO ADOLFO SIU MARQUEZ',
 'Laptop HP 240 G9', 1, 15900.00),
('GUSTAVO ADOLFO SIU MARQUEZ',
 'Teclado MSI Forge GK100 Combo', 1, 700.00),

('JOSE ALFREDO MEJIA GRANADOS',
 'Laptop ASUS E1504GA', 1, 13900.00),
('JOSE ALFREDO MEJIA GRANADOS',
 'Teclado Logitech G PRO', 1, 3500.00),

('NELSON JAVIER GUERRA NOLASCO',
 'Laptop MSI Modern 15', 1, 23900.00),
('NELSON JAVIER GUERRA NOLASCO',
 'Teclado Razer Huntsman Mini', 1, 3600.00),

('RAUL ANDRES RAUDALES GARCIA',
 'Laptop HP 240 G9', 1, 15900.00),
('RAUL ANDRES RAUDALES GARCIA',
 'Teclado Logitech G PRO', 2, 3500.00),

('RUT NOHEMY SANCHEZ GARCIA',
 'Laptop ASUS E1504GA', 1, 13900.00),
('RUT NOHEMY SANCHEZ GARCIA',
 'Teclado MSI Forge GK100 Combo', 2, 700.00),

('STANLEY LEMUEL GOFF STERBROOCK',
 'Laptop MSI Modern 15', 1, 23900.00),
('STANLEY LEMUEL GOFF STERBROOCK',
 'Teclado Razer Huntsman Mini', 2, 3600.00);

INSERT INTO dbo.orden_detalle
(orden_id, producto, cantidad, precio_unitario, subtotal)
SELECT
    o.id,
    p.producto,
    p.cantidad,
    p.precio,
    p.cantidad * p.precio
FROM @productos p
INNER JOIN dbo.ordenes o
    ON o.cliente = p.cliente
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.orden_detalle d
    WHERE d.orden_id = o.id
      AND d.producto = p.producto
);

UPDATE o
SET total = ISNULL((
    SELECT SUM(d.subtotal)
    FROM dbo.orden_detalle d
    WHERE d.orden_id = o.id
), 0)
FROM dbo.ordenes o;
GO

SELECT
    id,
    cliente,
    fecha,
    estado,
    total
FROM dbo.ordenes
ORDER BY id;

SELECT
    id,
    orden_id,
    producto,
    cantidad,
    precio_unitario,
    subtotal
FROM dbo.orden_detalle
ORDER BY orden_id, id;

SELECT
    (SELECT COUNT(*) FROM dbo.ordenes) AS total_ordenes,
    (SELECT COUNT(*) FROM dbo.orden_detalle) AS total_detalles,
    (SELECT ISNULL(SUM(total), 0) FROM dbo.ordenes) AS monto_total;
GO
