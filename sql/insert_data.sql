-- ===============================
-- Sample data for development/demo
-- ===============================

-- ===============================
-- ROLES
-- ===============================
INSERT INTO role (title) VALUES ('CUSTOMER') ON CONFLICT DO NOTHING;
INSERT INTO role (title) VALUES ('PARTNER') ON CONFLICT DO NOTHING;
INSERT INTO role (title) VALUES ('ADMIN') ON CONFLICT DO NOTHING;

-- ===============================
-- ACCOUNTS
-- Password hash bcrypt cho "123456": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G
-- ===============================

-- Admin account (id=1)
INSERT INTO account (username, password, status) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;

-- Customer accounts (id=2,3)
INSERT INTO account (username, password, status) VALUES 
('customer1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;
INSERT INTO account (username, password, status) VALUES 
('customer2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;

-- Partner accounts (id=4-13) - 10 cong ty du lich Viet Nam
INSERT INTO account (username, password, status) VALUES 
('vietravel', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;
INSERT INTO account (username, password, status) VALUES 
('saigontourist', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;
INSERT INTO account (username, password, status) VALUES 
('vinpearl', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;
INSERT INTO account (username, password, status) VALUES 
('sungroup', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;
INSERT INTO account (username, password, status) VALUES 
('fivitel', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;
INSERT INTO account (username, password, status) VALUES 
('muongthanh', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;
INSERT INTO account (username, password, status) VALUES 
('furama', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;
INSERT INTO account (username, password, status) VALUES 
('intercontinental', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;
INSERT INTO account (username, password, status) VALUES 
('anantara', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;
INSERT INTO account (username, password, status) VALUES 
('sixsenses', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5FhN5Oc5y5C2G', 'ACTIVE') ON CONFLICT DO NOTHING;

-- ===============================
-- CUSTOMERS
-- ===============================
INSERT INTO customer (account_id, fullname, email, phone_number, id_number) VALUES 
(2, 'Nguyễn Văn An', 'nguyenvanan@example.com', '0901234567', '012345678901') ON CONFLICT DO NOTHING;
INSERT INTO customer (account_id, fullname, email, phone_number, id_number) VALUES 
(3, 'Trần Thị Bình', 'tranthibinh@example.com', '0912345678', '012345678902') ON CONFLICT DO NOTHING;

-- ===============================
-- PARTNERS - 10 công ty du lịch Việt Nam
-- ===============================
INSERT INTO partner (account_id, name, phone_number, address, banking_number, bank, balance) VALUES 
(4, 'Vietravel Holdings', '0283930888', '190 Pasteur, Quận 3, TP.HCM', '0071001234567', 'Vietcombank', 50000000) ON CONFLICT DO NOTHING;
INSERT INTO partner (account_id, name, phone_number, address, banking_number, bank, balance) VALUES 
(5, 'Saigontourist Group', '0283829279', '23 Lê Lợi, Quận 1, TP.HCM', '0071002345678', 'BIDV', 80000000) ON CONFLICT DO NOTHING;
INSERT INTO partner (account_id, name, phone_number, address, banking_number, bank, balance) VALUES 
(6, 'Vinpearl Resort', '0243974999', '7 Bằng Lăng 1, Vinhomes Riverside, Hà Nội', '0071003456789', 'Techcombank', 120000000) ON CONFLICT DO NOTHING;
INSERT INTO partner (account_id, name, phone_number, address, banking_number, bank, balance) VALUES 
(7, 'Sun Group Tourism', '0243719999', '18 Hòa Mã, Hai Bà Trưng, Hà Nội', '0071004567890', 'VPBank', 150000000) ON CONFLICT DO NOTHING;
INSERT INTO partner (account_id, name, phone_number, address, banking_number, bank, balance) VALUES 
(8, 'FiviteL Hotels', '0243825888', '45 Nguyễn Chí Thanh, Đống Đa, Hà Nội', '0071005678901', 'MB Bank', 30000000) ON CONFLICT DO NOTHING;
INSERT INTO partner (account_id, name, phone_number, address, banking_number, bank, balance) VALUES 
(9, 'Mường Thanh Hospitality', '0243766888', '78 Trần Duy Hưng, Cầu Giấy, Hà Nội', '0071006789012', 'Agribank', 90000000) ON CONFLICT DO NOTHING;
INSERT INTO partner (account_id, name, phone_number, address, banking_number, bank, balance) VALUES 
(10, 'Furama Resort Vietnam', '0236395888', '105 Võ Nguyên Giáp, Ngũ Hành Sơn, Đà Nẵng', '0071007890123', 'Sacombank', 70000000) ON CONFLICT DO NOTHING;
INSERT INTO partner (account_id, name, phone_number, address, banking_number, bank, balance) VALUES 
(11, 'InterContinental Vietnam', '0283520999', '772 Điện Biên Phủ, Quận 10, TP.HCM', '0071008901234', 'ACB', 100000000) ON CONFLICT DO NOTHING;
INSERT INTO partner (account_id, name, phone_number, address, banking_number, bank, balance) VALUES 
(12, 'Anantara Vietnam', '0252384888', '1 Trần Hưng Đạo, Mũi Né, Phan Thiết', '0071009012345', 'TPBank', 60000000) ON CONFLICT DO NOTHING;
INSERT INTO partner (account_id, name, phone_number, address, banking_number, bank, balance) VALUES 
(13, 'Six Senses Vietnam', '0297398888', 'Đảo Hòn Thơm, Phú Quốc, Kiên Giang', '0071000123456', 'OCB', 200000000) ON CONFLICT DO NOTHING;

-- ===============================
-- CITIES
-- ===============================
INSERT INTO city (name) VALUES ('Hà Nội') ON CONFLICT DO NOTHING;
INSERT INTO city (name) VALUES ('Đà Nẵng') ON CONFLICT DO NOTHING;
INSERT INTO city (name) VALUES ('TP. Hồ Chí Minh') ON CONFLICT DO NOTHING;
INSERT INTO city (name) VALUES ('Nha Trang') ON CONFLICT DO NOTHING;
INSERT INTO city (name) VALUES ('Phú Quốc') ON CONFLICT DO NOTHING;
INSERT INTO city (name) VALUES ('Phan Thiết') ON CONFLICT DO NOTHING;
INSERT INTO city (name) VALUES ('Hội An') ON CONFLICT DO NOTHING;
INSERT INTO city (name) VALUES ('Đà Lạt') ON CONFLICT DO NOTHING;
INSERT INTO city (name) VALUES ('Hạ Long') ON CONFLICT DO NOTHING;
INSERT INTO city (name) VALUES ('Sapa') ON CONFLICT DO NOTHING;

-- ===============================
-- WARDS
-- ===============================
INSERT INTO ward (name, city_id) VALUES ('Quận Ba Đình', 1) ON CONFLICT DO NOTHING;
INSERT INTO ward (name, city_id) VALUES ('Quận Ngũ Hành Sơn', 2) ON CONFLICT DO NOTHING;
INSERT INTO ward (name, city_id) VALUES ('Quận 1', 3) ON CONFLICT DO NOTHING;
INSERT INTO ward (name, city_id) VALUES ('Phường Vĩnh Hòa', 4) ON CONFLICT DO NOTHING;
INSERT INTO ward (name, city_id) VALUES ('Thị trấn Dương Đông', 5) ON CONFLICT DO NOTHING;
INSERT INTO ward (name, city_id) VALUES ('Phường Mũi Né', 6) ON CONFLICT DO NOTHING;
INSERT INTO ward (name, city_id) VALUES ('Phường Cẩm Châu', 7) ON CONFLICT DO NOTHING;
INSERT INTO ward (name, city_id) VALUES ('Phường 3', 8) ON CONFLICT DO NOTHING;
INSERT INTO ward (name, city_id) VALUES ('Phường Bãi Cháy', 9) ON CONFLICT DO NOTHING;
INSERT INTO ward (name, city_id) VALUES ('Thị trấn Sa Pa', 10) ON CONFLICT DO NOTHING;


-- ===============================
-- RESORTS - 10 resorts với mô tả chi tiết
-- ===============================

-- Resort 1: Vietravel Nha Trang Beach Resort (partner_id=1)
INSERT INTO resort (partner_id, name, address, ward_id, img_360_url, rating) VALUES 
(1, 'Vietravel Nha Trang Beach Resort', '88 Trần Phú, Nha Trang', 4, 
'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=1200', 5) ON CONFLICT DO NOTHING;

-- Resort 2: Saigontourist Đà Nẵng Resort (partner_id=2)
INSERT INTO resort (partner_id, name, address, ward_id, img_360_url, rating) VALUES 
(2, 'Saigontourist Đà Nẵng Resort', '120 Võ Nguyên Giáp, Đà Nẵng', 2, 
'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1200', 5) ON CONFLICT DO NOTHING;

-- Resort 3: Vinpearl Phú Quốc Resort (partner_id=3)
INSERT INTO resort (partner_id, name, address, ward_id, img_360_url, rating) VALUES 
(3, 'Vinpearl Phú Quốc Resort', 'Bãi Dài, Phú Quốc', 5, 
'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=1200', 5) ON CONFLICT DO NOTHING;

-- Resort 4: Sun World Hạ Long Resort (partner_id=4)
INSERT INTO resort (partner_id, name, address, ward_id, img_360_url, rating) VALUES 
(4, 'Sun World Hạ Long Resort', '1 Hạ Long, Bãi Cháy', 9, 
'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=1200', 4) ON CONFLICT DO NOTHING;

-- Resort 5: FiviteL Đà Lạt Resort (partner_id=5)
INSERT INTO resort (partner_id, name, address, ward_id, img_360_url, rating) VALUES 
(5, 'FiviteL Đà Lạt Resort', '15 Trần Hưng Đạo, Đà Lạt', 8, 
'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=1200', 4) ON CONFLICT DO NOTHING;

-- Resort 6: Mường Thanh Sapa Resort (partner_id=6)
INSERT INTO resort (partner_id, name, address, ward_id, img_360_url, rating) VALUES 
(6, 'Mường Thanh Sapa Resort', '25 Fansipan, Sa Pa', 10, 
'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=1200', 4) ON CONFLICT DO NOTHING;

-- Resort 7: Furama Đà Nẵng Resort (partner_id=7)
INSERT INTO resort (partner_id, name, address, ward_id, img_360_url, rating) VALUES 
(7, 'Furama Đà Nẵng Resort', '105 Võ Nguyên Giáp, Đà Nẵng', 2, 
'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=1200', 5) ON CONFLICT DO NOTHING;

-- Resort 8: InterContinental Hội An (partner_id=8)
INSERT INTO resort (partner_id, name, address, ward_id, img_360_url, rating) VALUES 
(8, 'InterContinental Hội An Resort', 'Block B, Cẩm Châu, Hội An', 7, 
'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=1200', 5) ON CONFLICT DO NOTHING;

-- Resort 9: Anantara Mũi Né Resort (partner_id=9)
INSERT INTO resort (partner_id, name, address, ward_id, img_360_url, rating) VALUES 
(9, 'Anantara Mũi Né Resort', '1 Trần Hưng Đạo, Mũi Né', 6, 
'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=1200', 5) ON CONFLICT DO NOTHING;

-- Resort 10: Six Senses Côn Đảo (partner_id=10)
INSERT INTO resort (partner_id, name, address, ward_id, img_360_url, rating) VALUES 
(10, 'Six Senses Côn Đảo Resort', 'Đảo Côn Sơn, Côn Đảo', 5, 
'https://images.unsplash.com/photo-1573052905904-34ad8c27f0cc?w=1200', 5) ON CONFLICT DO NOTHING;

-- ===============================
-- RESORT IMAGES (3-4 hình/resort)
-- ===============================

-- Resort 1 images
INSERT INTO resort_images (resort_id, url) VALUES (1, 'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (1, 'https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (1, 'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (1, 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800') ON CONFLICT DO NOTHING;

-- Resort 2 images
INSERT INTO resort_images (resort_id, url) VALUES (2, 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (2, 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (2, 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800') ON CONFLICT DO NOTHING;

-- Resort 3 images
INSERT INTO resort_images (resort_id, url) VALUES (3, 'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (3, 'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (3, 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (3, 'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800') ON CONFLICT DO NOTHING;

-- Resort 4 images
INSERT INTO resort_images (resort_id, url) VALUES (4, 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (4, 'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (4, 'https://images.unsplash.com/photo-1573052905904-34ad8c27f0cc?w=800') ON CONFLICT DO NOTHING;

-- Resort 5 images
INSERT INTO resort_images (resort_id, url) VALUES (5, 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (5, 'https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (5, 'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (5, 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800') ON CONFLICT DO NOTHING;

-- Resort 6 images
INSERT INTO resort_images (resort_id, url) VALUES (6, 'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (6, 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (6, 'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800') ON CONFLICT DO NOTHING;

-- Resort 7 images
INSERT INTO resort_images (resort_id, url) VALUES (7, 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (7, 'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (7, 'https://images.unsplash.com/photo-1573052905904-34ad8c27f0cc?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (7, 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800') ON CONFLICT DO NOTHING;

-- Resort 8 images
INSERT INTO resort_images (resort_id, url) VALUES (8, 'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (8, 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (8, 'https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800') ON CONFLICT DO NOTHING;

-- Resort 9 images
INSERT INTO resort_images (resort_id, url) VALUES (9, 'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (9, 'https://images.unsplash.com/photo-1573052905904-34ad8c27f0cc?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (9, 'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (9, 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800') ON CONFLICT DO NOTHING;

-- Resort 10 images
INSERT INTO resort_images (resort_id, url) VALUES (10, 'https://images.unsplash.com/photo-1573052905904-34ad8c27f0cc?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (10, 'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800') ON CONFLICT DO NOTHING;
INSERT INTO resort_images (resort_id, url) VALUES (10, 'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800') ON CONFLICT DO NOTHING;


-- ===============================
-- ROOM TYPES (3 loại phòng/resort: Standard, Deluxe, Suite)
-- ===============================

-- Resort 1 room types
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(1, 'Standard', 28.0, 'Tiêu chuẩn', 'Thoải mái', 1, 2, 1200000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(1, 'Deluxe', 40.0, 'Cao cấp', 'Sang trọng', 2, 4, 2200000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(1, 'Suite', 65.0, 'Đặc biệt', 'Thượng hạng', 3, 6, 4500000) ON CONFLICT DO NOTHING;

-- Resort 2 room types
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(2, 'Standard', 30.0, 'Tiêu chuẩn', 'Thoải mái', 1, 2, 1500000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(2, 'Deluxe', 45.0, 'Cao cấp', 'Sang trọng', 2, 4, 2800000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(2, 'Suite', 70.0, 'Đặc biệt', 'Thượng hạng', 3, 6, 5200000) ON CONFLICT DO NOTHING;

-- Resort 3 room types
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(3, 'Standard', 32.0, 'Tiêu chuẩn', 'Thoải mái', 1, 2, 1800000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(3, 'Deluxe', 50.0, 'Cao cấp', 'Sang trọng', 2, 4, 3500000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(3, 'Suite', 80.0, 'Đặc biệt', 'Thượng hạng', 3, 6, 6500000) ON CONFLICT DO NOTHING;

-- Resort 4 room types
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(4, 'Standard', 26.0, 'Tiêu chuẩn', 'Thoải mái', 1, 2, 1100000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(4, 'Deluxe', 38.0, 'Cao cấp', 'Sang trọng', 2, 4, 2000000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(4, 'Suite', 60.0, 'Đặc biệt', 'Thượng hạng', 3, 6, 4000000) ON CONFLICT DO NOTHING;

-- Resort 5 room types
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(5, 'Standard', 25.0, 'Tiêu chuẩn', 'Thoải mái', 1, 2, 900000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(5, 'Deluxe', 35.0, 'Cao cấp', 'Sang trọng', 2, 4, 1600000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(5, 'Suite', 55.0, 'Đặc biệt', 'Thượng hạng', 3, 6, 3200000) ON CONFLICT DO NOTHING;

-- Resort 6 room types
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(6, 'Standard', 24.0, 'Tiêu chuẩn', 'Thoải mái', 1, 2, 850000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(6, 'Deluxe', 36.0, 'Cao cấp', 'Sang trọng', 2, 4, 1500000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(6, 'Suite', 52.0, 'Đặc biệt', 'Thượng hạng', 3, 6, 2800000) ON CONFLICT DO NOTHING;

-- Resort 7 room types
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(7, 'Standard', 35.0, 'Tiêu chuẩn', 'Thoải mái', 1, 2, 2000000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(7, 'Deluxe', 55.0, 'Cao cấp', 'Sang trọng', 2, 4, 3800000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(7, 'Suite', 85.0, 'Đặc biệt', 'Thượng hạng', 3, 6, 7000000) ON CONFLICT DO NOTHING;

-- Resort 8 room types
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(8, 'Standard', 38.0, 'Tiêu chuẩn', 'Thoải mái', 1, 2, 2500000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(8, 'Deluxe', 60.0, 'Cao cấp', 'Sang trọng', 2, 4, 4500000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(8, 'Suite', 95.0, 'Đặc biệt', 'Thượng hạng', 3, 6, 8500000) ON CONFLICT DO NOTHING;

-- Resort 9 room types
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(9, 'Standard', 40.0, 'Tiêu chuẩn', 'Thoải mái', 1, 2, 2800000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(9, 'Deluxe', 65.0, 'Cao cấp', 'Sang trọng', 2, 4, 5000000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(9, 'Suite', 100.0, 'Đặc biệt', 'Thượng hạng', 3, 6, 9500000) ON CONFLICT DO NOTHING;

-- Resort 10 room types
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(10, 'Standard', 45.0, 'Tiêu chuẩn', 'Thoải mái', 1, 2, 3500000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(10, 'Deluxe', 75.0, 'Cao cấp', 'Sang trọng', 2, 4, 6500000) ON CONFLICT DO NOTHING;
INSERT INTO room_type (resort_id, name, area, quantity_standard, quality_standard, bed_amount, people_amount, price) VALUES 
(10, 'Suite', 120.0, 'Đặc biệt', 'Thượng hạng', 3, 6, 12000000) ON CONFLICT DO NOTHING;


-- ===============================
-- ROOM IMAGES (2 hình/loại phòng)
-- ===============================

-- Resort 1 room images (room_type_id 1-3)
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (1, 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (1, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (2, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (2, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (3, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (3, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800', FALSE) ON CONFLICT DO NOTHING;

-- Resort 2 room images (room_type_id 4-6)
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (4, 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (4, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (5, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (5, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (6, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (6, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800', FALSE) ON CONFLICT DO NOTHING;

-- Resort 3 room images (room_type_id 7-9)
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (7, 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (7, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (8, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (8, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (9, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (9, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800', FALSE) ON CONFLICT DO NOTHING;

-- Resort 4 room images (room_type_id 10-12)
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (10, 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (10, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (11, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (11, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (12, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (12, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800', FALSE) ON CONFLICT DO NOTHING;

-- Resort 5 room images (room_type_id 13-15)
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (13, 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (13, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (14, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (14, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (15, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (15, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800', FALSE) ON CONFLICT DO NOTHING;

-- Resort 6 room images (room_type_id 16-18)
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (16, 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (16, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (17, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (17, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (18, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (18, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800', FALSE) ON CONFLICT DO NOTHING;

-- Resort 7 room images (room_type_id 19-21)
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (19, 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (19, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (20, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (20, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (21, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (21, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800', FALSE) ON CONFLICT DO NOTHING;

-- Resort 8 room images (room_type_id 22-24)
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (22, 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (22, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (23, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (23, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (24, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (24, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800', FALSE) ON CONFLICT DO NOTHING;

-- Resort 9 room images (room_type_id 25-27)
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (25, 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (25, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (26, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (26, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (27, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (27, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800', FALSE) ON CONFLICT DO NOTHING;

-- Resort 10 room images (room_type_id 28-30)
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (28, 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (28, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (29, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (29, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (30, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800', FALSE) ON CONFLICT DO NOTHING;
INSERT INTO room_images (room_type_id, url, is_deleted) VALUES (30, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800', FALSE) ON CONFLICT DO NOTHING;


-- ===============================
-- ROOMS (2 phòng/loại phòng)
-- ===============================

-- Resort 1 rooms
INSERT INTO room (room_type_id, number, status) VALUES (1, 101, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (1, 102, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (2, 201, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (2, 202, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (3, 301, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (3, 302, 'available') ON CONFLICT DO NOTHING;

-- Resort 2 rooms
INSERT INTO room (room_type_id, number, status) VALUES (4, 101, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (4, 102, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (5, 201, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (5, 202, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (6, 301, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (6, 302, 'available') ON CONFLICT DO NOTHING;

-- Resort 3 rooms
INSERT INTO room (room_type_id, number, status) VALUES (7, 101, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (7, 102, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (8, 201, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (8, 202, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (9, 301, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (9, 302, 'available') ON CONFLICT DO NOTHING;

-- Resort 4 rooms
INSERT INTO room (room_type_id, number, status) VALUES (10, 101, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (10, 102, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (11, 201, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (11, 202, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (12, 301, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (12, 302, 'available') ON CONFLICT DO NOTHING;

-- Resort 5 rooms
INSERT INTO room (room_type_id, number, status) VALUES (13, 101, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (13, 102, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (14, 201, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (14, 202, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (15, 301, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (15, 302, 'available') ON CONFLICT DO NOTHING;

-- Resort 6 rooms
INSERT INTO room (room_type_id, number, status) VALUES (16, 101, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (16, 102, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (17, 201, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (17, 202, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (18, 301, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (18, 302, 'available') ON CONFLICT DO NOTHING;

-- Resort 7 rooms
INSERT INTO room (room_type_id, number, status) VALUES (19, 101, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (19, 102, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (20, 201, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (20, 202, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (21, 301, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (21, 302, 'available') ON CONFLICT DO NOTHING;

-- Resort 8 rooms
INSERT INTO room (room_type_id, number, status) VALUES (22, 101, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (22, 102, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (23, 201, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (23, 202, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (24, 301, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (24, 302, 'available') ON CONFLICT DO NOTHING;

-- Resort 9 rooms
INSERT INTO room (room_type_id, number, status) VALUES (25, 101, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (25, 102, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (26, 201, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (26, 202, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (27, 301, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (27, 302, 'available') ON CONFLICT DO NOTHING;

-- Resort 10 rooms
INSERT INTO room (room_type_id, number, status) VALUES (28, 101, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (28, 102, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (29, 201, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (29, 202, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (30, 301, 'available') ON CONFLICT DO NOTHING;
INSERT INTO room (room_type_id, number, status) VALUES (30, 302, 'available') ON CONFLICT DO NOTHING;

-- ===============================
-- SERVICES (Spa, Gym, Pool, Restaurant cho mỗi resort)
-- ===============================

-- Resort 1 services
INSERT INTO service (name, resort_id) VALUES ('Spa & Massage', 1) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Phòng Gym', 1) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Hồ bơi vô cực', 1) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Nhà hàng hải sản', 1) ON CONFLICT DO NOTHING;

-- Resort 2 services
INSERT INTO service (name, resort_id) VALUES ('Spa & Massage', 2) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Phòng Gym', 2) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Hồ bơi ngoài trời', 2) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Nhà hàng Á-Âu', 2) ON CONFLICT DO NOTHING;

-- Resort 3 services
INSERT INTO service (name, resort_id) VALUES ('Spa cao cấp', 3) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Fitness Center', 3) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Hồ bơi riêng', 3) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Nhà hàng 5 sao', 3) ON CONFLICT DO NOTHING;

-- Resort 4 services
INSERT INTO service (name, resort_id) VALUES ('Spa thư giãn', 4) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Phòng tập thể dục', 4) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Hồ bơi trong nhà', 4) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Nhà hàng buffet', 4) ON CONFLICT DO NOTHING;

-- Resort 5 services
INSERT INTO service (name, resort_id) VALUES ('Spa núi rừng', 5) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Gym hiện đại', 5) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Hồ bơi nước ấm', 5) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Nhà hàng đặc sản', 5) ON CONFLICT DO NOTHING;

-- Resort 6 services
INSERT INTO service (name, resort_id) VALUES ('Spa truyền thống', 6) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Phòng Gym', 6) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Hồ bơi sưởi ấm', 6) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Nhà hàng Tây Bắc', 6) ON CONFLICT DO NOTHING;

-- Resort 7 services
INSERT INTO service (name, resort_id) VALUES ('Spa biển', 7) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Fitness Center', 7) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Hồ bơi vô cực', 7) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Nhà hàng hải sản cao cấp', 7) ON CONFLICT DO NOTHING;

-- Resort 8 services
INSERT INTO service (name, resort_id) VALUES ('Spa thảo dược', 8) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Gym cao cấp', 8) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Hồ bơi riêng biệt', 8) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Nhà hàng Hội An', 8) ON CONFLICT DO NOTHING;

-- Resort 9 services
INSERT INTO service (name, resort_id) VALUES ('Spa sang trọng', 9) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Fitness & Yoga', 9) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Hồ bơi biển', 9) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Nhà hàng quốc tế', 9) ON CONFLICT DO NOTHING;

-- Resort 10 services
INSERT INTO service (name, resort_id) VALUES ('Spa thiên nhiên', 10) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Wellness Center', 10) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Hồ bơi tự nhiên', 10) ON CONFLICT DO NOTHING;
INSERT INTO service (name, resort_id) VALUES ('Nhà hàng organic', 10) ON CONFLICT DO NOTHING;


-- ===============================
-- OFFERS (1 offer cho mỗi loại phòng)
-- ===============================

-- Resort 1 offers
INSERT INTO offer (room_type_id, cost) VALUES (1, 1200000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (2, 2200000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (3, 4500000) ON CONFLICT DO NOTHING;

-- Resort 2 offers
INSERT INTO offer (room_type_id, cost) VALUES (4, 1500000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (5, 2800000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (6, 5200000) ON CONFLICT DO NOTHING;

-- Resort 3 offers
INSERT INTO offer (room_type_id, cost) VALUES (7, 1800000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (8, 3500000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (9, 6500000) ON CONFLICT DO NOTHING;

-- Resort 4 offers
INSERT INTO offer (room_type_id, cost) VALUES (10, 1100000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (11, 2000000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (12, 4000000) ON CONFLICT DO NOTHING;

-- Resort 5 offers
INSERT INTO offer (room_type_id, cost) VALUES (13, 900000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (14, 1600000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (15, 3200000) ON CONFLICT DO NOTHING;

-- Resort 6 offers
INSERT INTO offer (room_type_id, cost) VALUES (16, 850000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (17, 1500000) ON CONFLICT DO NOTHING;
IN
SERT INTO offer (room_type_id, cost) VALUES (18, 2800000) ON CONFLICT DO NOTHING;

-- Resort 7 offers
INSERT INTO offer (room_type_id, cost) VALUES (19, 2000000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (20, 3800000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (21, 7000000) ON CONFLICT DO NOTHING;

-- Resort 8 offers
INSERT INTO offer (room_type_id, cost) VALUES (22, 2500000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (23, 4500000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (24, 8500000) ON CONFLICT DO NOTHING;

-- Resort 9 offers
INSERT INTO offer (room_type_id, cost) VALUES (25, 2800000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (26, 5000000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (27, 9500000) ON CONFLICT DO NOTHING;

-- Resort 10 offers
INSERT INTO offer (room_type_id, cost) VALUES (28, 3500000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (29, 6500000) ON CONFLICT DO NOTHING;
INSERT INTO offer (room_type_id, cost) VALUES (30, 12000000) ON CONFLICT DO NOTHING;

-- ===============================
-- FEEDBACKS (2-3 binh luan/resort bang tieng Viet)
-- ===============================

-- Resort 1 feedbacks
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 1, 5, 'Resort tuyet voi! View bien dep lung linh, nhan vien phuc vu nhiet tinh va chuyen nghiep. Phong sach se, tien nghi day du. Bua sang buffet da dang mon an. Chac chan se quay lai lan sau!', NOW() - INTERVAL '30 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(2, 1, 4, 'Ky nghi tuyet voi cung gia dinh. Ho boi rong rai, tre con rat thich. Dich vu spa thu gian sau mot ngay dai. Gia ca hop ly so voi chat luong nhan duoc.', NOW() - INTERVAL '15 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 1, 5, 'Day la lan thu 3 minh den day va lan nao cung hai long. Vi tri dac dia, gan bien, do an ngon. Nhan vien nho ten khach quen, rat chu dao!', NOW() - INTERVAL '5 days') ON CONFLICT DO NOTHING;

-- Resort 2 feedbacks
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 2, 5, 'Resort dang cap 5 sao thuc su! Kien truc doc dao, khong gian xanh mat. Bai bien rieng sach dep. Nha hang phuc vu mon an Viet Nam va quoc te deu ngon. Rat dang tien!', NOW() - INTERVAL '25 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(2, 2, 5, 'Honeymoon tai day that tuyet voi! Phong suite view bien lang man, co bon tam jacuzzi. Duoc tang hoa va ruou vang khi check-in. Dich vu hoan hao!', NOW() - INTERVAL '10 days') ON CONFLICT DO NOTHING;

-- Resort 3 feedbacks
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 3, 5, 'Vinpearl khong lam that vong! Khu vui choi giai tri da dang, phu hop cho ca gia dinh. Phong rong rai, view dep. Buffet sang phong phu voi hon 100 mon.', NOW() - INTERVAL '20 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(2, 3, 4, 'Resort sang trong, tien nghi hien dai. Ho boi vo cuc tuyet dep. Chi tiec la hoi dong khach vao cuoi tuan. Nen dat phong som de co gia tot.', NOW() - INTERVAL '8 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 3, 5, 'Lan dau den Phu Quoc va chon Vinpearl la quyet dinh dung dan. Nhan vien than thien, ho tro nhiet tinh. Bai bien rieng cuc ky sach va dep!', NOW() - INTERVAL '3 days') ON CONFLICT DO NOTHING;

-- Resort 4 feedbacks
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 4, 4, 'View vinh Ha Long tu phong dep khong tuong! Thuc day ngam binh minh tren vinh la trai nghiem kho quen. Dich vu tour du thuyen rat chuyen nghiep.', NOW() - INTERVAL '18 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(2, 4, 4, 'Resort co vi tri tuyet voi de kham pha Ha Long. Phong thoang mat, sach se. Nha hang hai san tuoi ngon. Gia ca phai chang cho chat luong 4 sao.', NOW() - INTERVAL '7 days') ON CONFLICT DO NOTHING;

-- Resort 5 feedbacks
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 5, 4, 'Da Lat mong mo, resort am cung! Khong gian yen tinh, thich hop nghi duong. Ho boi nuoc am rat thich vao buoi sang se lanh. Do an ngon, dac biet la lau ga la e.', NOW() - INTERVAL '22 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(2, 5, 5, 'Ky nghi lang man tai thanh pho ngan hoa. Resort co vuon hoa dep, chup anh cuc chat. Phong co lo suoi, am ap vao ban dem. Se quay lai vao mua hoa!', NOW() - INTERVAL '12 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 5, 4, 'Gia tot cho chat luong nhan duoc. Nhan vien nhiet tinh, ho tro dat tour tham quan. Bua sang co banh mi Da Lat nong gion rat ngon!', NOW() - INTERVAL '2 days') ON CONFLICT DO NOTHING;

-- Resort 6 feedbacks
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 6, 4, 'Sapa dep nhu tranh ve! Resort nam tren doi, view ruong bac thang tuyet dep. Phong am ap, co ban cong ngam canh. Spa truyen thong voi thao duoc dia phuong rat thu gian.', NOW() - INTERVAL '28 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(2, 6, 4, 'Trai nghiem van hoa Tay Bac doc dao. Nha hang phuc vu mon an dan toc ngon. Nhan vien la nguoi dia phuong, than thien va hieu biet ve van hoa vung cao.', NOW() - INTERVAL '14 days') ON CONFLICT DO NOTHING;

-- Resort 7 feedbacks
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 7, 5, 'Furama xung dang la resort hang dau Da Nang! Kien truc Cham Pa doc dao, bai bien rieng dai va sach. Dich vu 5 sao thuc su, nhan vien chuyen nghiep.', NOW() - INTERVAL '24 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(2, 7, 5, 'Da o nhieu resort nhung Furama van la so 1! Ho boi vo cuc view bien tuyet dep. Buffet hai san toi thu 7 phong phu va tuoi ngon. Highly recommend!', NOW() - INTERVAL '9 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 7, 5, 'Ky niem 10 nam ngay cuoi tai day, duoc resort tang banh va hoa. Cam dong voi su chu dao cua nhan vien. Phong suite co bon tam view bien lang man!', NOW() - INTERVAL '1 day') ON CONFLICT DO NOTHING;

-- Resort 8 feedbacks
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 8, 5, 'InterContinental Hoi An la thien duong nghi duong! Kien truc hai hoa voi thien nhien, co vuon thao moc rieng. Spa thao duoc tuyet voi, da min mang sau khi massage.', NOW() - INTERVAL '26 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(2, 8, 5, 'Resort yen tinh, thich hop cho nguoi muon tranh xa on ao. Co xe dua don mien phi vao pho co. Nha hang phuc vu mon Hoi An authentic, dac biet la cao lau va mi Quang.', NOW() - INTERVAL '11 days') ON CONFLICT DO NOTHING;

-- Resort 9 feedbacks
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 9, 5, 'Anantara Mui Ne sang trong va rieng tu! Villa co ho boi rieng, khong gian yen tinh. Bai bien dep, nuoc trong xanh. Dich vu butler chu dao tung chi tiet nho.', NOW() - INTERVAL '21 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(2, 9, 5, 'Honeymoon hoan hao! Duoc setup romantic dinner tren bai bien, nen va hoa hong. Spa couple massage thu gian. Nhan vien nho ten va so thich cua khach.', NOW() - INTERVAL '6 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 9, 4, 'Resort dep, dich vu tot nhung gia hoi cao. Phu hop cho dip dac biet. Bua sang buffet da dang, co ca mon Viet va quoc te. View binh minh tu phong tuyet dep!', NOW() - INTERVAL '4 days') ON CONFLICT DO NOTHING;

-- Resort 10 feedbacks
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 10, 5, 'Six Senses la dinh nghia cua luxury! Moi thu deu organic va ben vung. Villa rieng biet giua thien nhien hoang so. Trai nghiem detox va wellness tuyet voi.', NOW() - INTERVAL '19 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(2, 10, 5, 'Dat nhung xung dang tung dong! Dich vu ca nhan hoa, nhan vien nho moi so thich cua khach. Do an organic tuoi ngon, co vuon rau rieng cua resort. Thien duong nghi duong!', NOW() - INTERVAL '13 days') ON CONFLICT DO NOTHING;
INSERT INTO feedback (customer_id, resort_id, rating, comment, created_at) VALUES 
(1, 10, 5, 'Lan dau trai nghiem resort 6 sao va khong that vong. Moi chi tiet deu hoan hao tu phong, do an den dich vu. Se tiet kiem de quay lai lan nua!', NOW() - INTERVAL '2 days') ON CONFLICT DO NOTHING;

-- ===============================
-- ACCOUNT ASSIGN ROLES
-- ===============================

-- Admin role (role_id=3)
INSERT INTO account_assign_role (account_id, role_id) VALUES (1, 3) ON CONFLICT DO NOTHING;

-- Customer roles (role_id=1)
INSERT INTO account_assign_role (account_id, role_id) VALUES (2, 1) ON CONFLICT DO NOTHING;
INSERT INTO account_assign_role (account_id, role_id) VALUES (3, 1) ON CONFLICT DO NOTHING;

-- Partner roles (role_id=2)
INSERT INTO account_assign_role (account_id, role_id) VALUES (4, 2) ON CONFLICT DO NOTHING;
INSERT INTO account_assign_role (account_id, role_id) VALUES (5, 2) ON CONFLICT DO NOTHING;
INSERT INTO account_assign_role (account_id, role_id) VALUES (6, 2) ON CONFLICT DO NOTHING;
INSERT INTO account_assign_role (account_id, role_id) VALUES (7, 2) ON CONFLICT DO NOTHING;
INSERT INTO account_assign_role (account_id, role_id) VALUES (8, 2) ON CONFLICT DO NOTHING;
INSERT INTO account_assign_role (account_id, role_id) VALUES (9, 2) ON CONFLICT DO NOTHING;
INSERT INTO account_assign_role (account_id, role_id) VALUES (10, 2) ON CONFLICT DO NOTHING;
INSERT INTO account_assign_role (account_id, role_id) VALUES (11, 2) ON CONFLICT DO NOTHING;
INSERT INTO account_assign_role (account_id, role_id) VALUES (12, 2) ON CONFLICT DO NOTHING;
INSERT INTO account_assign_role (account_id, role_id) VALUES (13, 2) ON CONFLICT DO NOTHING;
