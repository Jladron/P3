/* TRIGGER para evitar la creación de una sucursal usando una dirección postal ya asignada. */

DELIMITER $$
CREATE TRIGGER nuevaSucursal_direccion
    BEFORE INSERT on SUCURSALES
    FOR EACH ROW
BEGIN
    IF EXISTS (SELECT DIRECCION FROM SUCURSALES WHERE DIRECCION = ('"+DIRECCION+"')) THEN
        signal sqlstate '23000' set message_text = 'La dirección postal introducida se encuentra en uso. Introduzca una nueva para poder completar el proceso.';
    END IF;
END $$

DELIMITER ;

/* TRIGGER para evitar la creación de una sucursal usando un ID ya generado anteriormente. */

DELIMITER $$
CREATE TRIGGER nuevaSucursal_ID
    BEFORE INSERT on SUCURSALES
    FOR EACH ROW
BEGIN
    IF EXISTS (SELECT ID_Sucursal FROM SUCURSALES WHERE ID_Sucursal = ('"+ID_Sucursal+"')) THEN
        signal sqlstate '23600' set message_text = 'Ha fallado el proceso de asignación de ID para la sucursal. Inténtelo de nuevo';
    END IF;
END $$

DELIMITER ;