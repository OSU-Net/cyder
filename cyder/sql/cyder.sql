ALTER TABLE `address_record` CHANGE `ip_upper` `ip_upper` BIGINT( 64 ) UNSIGNED;
ALTER TABLE `address_record` CHANGE `ip_lower` `ip_lower` BIGINT( 64 ) UNSIGNED;

ALTER TABLE `network` CHANGE `start_upper` `start_upper` BIGINT( 64 ) UNSIGNED;
ALTER TABLE `network` CHANGE `start_lower` `start_lower` BIGINT( 64 ) UNSIGNED;
ALTER TABLE `network` CHANGE `end_upper` `end_upper` BIGINT( 64 ) UNSIGNED;
ALTER TABLE `network` CHANGE `end_lower` `end_lower` BIGINT( 64 ) UNSIGNED;

ALTER TABLE `supernet` CHANGE `start_upper` `start_upper` BIGINT( 64 ) UNSIGNED;
ALTER TABLE `supernet` CHANGE `start_lower` `start_lower` BIGINT( 64 ) UNSIGNED;
ALTER TABLE `supernet` CHANGE `end_upper` `end_upper` BIGINT( 64 ) UNSIGNED;
ALTER TABLE `supernet` CHANGE `end_lower` `end_lower` BIGINT( 64 ) UNSIGNED;

ALTER TABLE `ptr` CHANGE `ip_upper` `ip_upper` BIGINT( 64 ) UNSIGNED NOT NULL;
ALTER TABLE `ptr` CHANGE `ip_lower` `ip_lower` BIGINT( 64 ) UNSIGNED NOT NULL;

ALTER TABLE `range` CHANGE `start_upper` `start_upper` BIGINT( 64 ) UNSIGNED;
ALTER TABLE `range` CHANGE `start_lower` `start_lower` BIGINT( 64 ) UNSIGNED;
ALTER TABLE `range` CHANGE `end_upper` `end_upper` BIGINT( 64 ) UNSIGNED;
ALTER TABLE `range` CHANGE `end_lower` `end_lower` BIGINT( 64 ) UNSIGNED;
