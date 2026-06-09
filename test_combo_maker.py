import unittest
import os
import tempfile
import hashlib
import re
from datetime import datetime

class TestCredentialExtraction(unittest.TestCase):
    """Test credential extraction functionality"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.test_dir)
    
    def test_android_combo_extraction(self):
        """Test Android package combo extraction"""
        test_content = "com.example.app:user@email.com:password123\n"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            pattern = r'^([a-z][a-z0-9_\.]+):([^:]+):(.+)$'
            match = re.match(pattern, content.strip())
            
            self.assertIsNotNone(match)
            self.assertEqual(match.group(1), "com.example.app")
            self.assertEqual(match.group(2), "user@email.com")
            self.assertEqual(match.group(3), "password123")
    
    def test_email_extraction(self):
        """Test email pattern extraction"""
        test_content = "user@example.com:password\njohn.doe@company.co.uk:pass123\n"
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        lines = test_content.splitlines()
        for line in lines:
            if ':' in line:
                email = line.split(':')[0]
                self.assertTrue(re.match(email_pattern, email) is not None)
    
    def test_jwt_extraction(self):
        """Test JWT token extraction"""
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        jwt_pattern = r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'
        
        matches = re.findall(jwt_pattern, jwt)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], jwt)
    
    def test_credit_card_luhn(self):
        """Test credit card Luhn algorithm"""
        def luhn_check(card_number):
            card_number = re.sub(r'\D', '', card_number)
            if not card_number.isdigit() or len(card_number) < 13:
                return False
            total = 0
            reverse_digits = card_number[::-1]
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n = n - 9
                total += n
            return total % 10 == 0
        
        # Valid test card numbers
        valid_cards = [
            "4111111111111111",  # Visa
            "5555555555554444",  # Mastercard
            "378282246310005",   # Amex
            "6011111111111117"   # Discover
        ]
        
        for card in valid_cards:
            self.assertTrue(luhn_check(card), f"Card {card} should be valid")
        
        # Invalid test card numbers
        invalid_cards = [
            "1234567890123456",
            "4111111111111112",
            "0000000000000000"
        ]
        
        for card in invalid_cards:
            self.assertFalse(luhn_check(card), f"Card {card} should be invalid")
    
    def test_phone_extraction(self):
        """Test phone number extraction and validation"""
        def clean_phone(number):
            return re.sub(r'[^\d+]', '', str(number))
        
        def is_valid_mobile(number):
            clean = clean_phone(number)
            return 7 <= len(clean) <= 15
        
        test_numbers = [
            "+1234567890",
            "9876543210",
            "123-456-7890",
            "+91 9876543210"
        ]
        
        for number in test_numbers:
            self.assertTrue(is_valid_mobile(number))

class TestDuplicateDetection(unittest.TestCase):
    """Test duplicate detection functionality"""
    
    def test_credential_hashing(self):
        """Test credential hash generation"""
        def get_credential_hash(username, password):
            return hashlib.md5(f"{username}:{password}".encode()).hexdigest()
        
        hash1 = get_credential_hash("user1", "pass1")
        hash2 = get_credential_hash("user1", "pass1")
        hash3 = get_credential_hash("user2", "pass2")
        
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)
    
    def test_file_hashing(self):
        """Test file hash generation for duplicate detection"""
        def get_file_hash(file_path):
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                chunk = f.read(65536)
                sha256.update(chunk)
            return sha256.hexdigest()
        
        test_content = "This is test content"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            f1.write(test_content)
            f1_path = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            f2.write(test_content)
            f2_path = f2.name
        
        hash1 = get_file_hash(f1_path)
        hash2 = get_file_hash(f2_path)
        
        self.assertEqual(hash1, hash2)
        
        os.remove(f1_path)
        os.remove(f2_path)

class TestFileHandling(unittest.TestCase):
    """Test file handling features"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)
    
    def test_binary_detection(self):
        """Test binary file detection"""
        def is_binary(file_path):
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:
                    return True
            return False
        
        # Create text file
        text_file = os.path.join(self.test_dir, "test.txt")
        with open(text_file, 'w') as f:
            f.write("This is a text file")
        
        self.assertFalse(is_binary(text_file))
        
        # Create binary-like file
        binary_file = os.path.join(self.test_dir, "test.bin")
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03')
        
        self.assertTrue(is_binary(binary_file))
    
    def test_file_size_limit(self):
        """Test file size limit checking"""
        def is_size_allowed(file_path, max_mb):
            if max_mb == 0:
                return True
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)
            return size_mb <= max_mb
        
        # Create 1KB file
        small_file = os.path.join(self.test_dir, "small.txt")
        with open(small_file, 'wb') as f:
            f.write(b'x' * 1024)
        
        self.assertTrue(is_size_allowed(small_file, 0))
        self.assertTrue(is_size_allowed(small_file, 10))
        self.assertTrue(is_size_allowed(small_file, 0.001))
        
        # Create 2MB file
        large_file = os.path.join(self.test_dir, "large.txt")
        with open(large_file, 'wb') as f:
            f.write(b'x' * (2 * 1024 * 1024))
        
        self.assertTrue(is_size_allowed(large_file, 0))
        self.assertFalse(is_size_allowed(large_file, 1))
        self.assertTrue(is_size_allowed(large_file, 3))

class TestRegexPatterns(unittest.TestCase):
    """Test regex pattern matching for various data types"""
    
    def test_gift_card_patterns(self):
        """Test gift card pattern matching"""
        patterns = {
            'amazon': r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}',
            'google_play': r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}'
        }
        
        test_cases = [
            ("ABCD-1234-EFGH-5678", 'amazon'),
            ("ABCD-1234-EFGH-5678-IJKL", 'google_play'),
        ]
        
        for test_str, pattern_name in test_cases:
            pattern = patterns[pattern_name]
            self.assertTrue(re.match(pattern, test_str) is not None)
    
    def test_api_key_patterns(self):
        """Test API key pattern matching"""
        patterns = {
            'aws': r'AKIA[0-9A-Z]{16}',
            'google': r'AIza[0-9A-Za-z\-_]{35}',
            'github': r'ghp_[0-9a-zA-Z]{36}'
        }
        
        test_cases = [
            ("AKIAIOSFODNN7EXAMPLE", 'aws'),
            ("AIzaSyA1234567890abcdefghijklmnopqrstuvwxyz", 'google'),
            ("ghp_abcdefghijklmnopqrstuvwxyz1234567890", 'github')
        ]
        
        for test_str, pattern_name in test_cases:
            pattern = patterns[pattern_name]
            self.assertTrue(re.match(pattern, test_str) is not None)
    
    def test_crypto_wallet_patterns(self):
        """Test cryptocurrency wallet pattern matching"""
        patterns = {
            'bitcoin': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
            'ethereum': r'\b0x[a-fA-F0-9]{40}\b'
        }
        
        test_cases = [
            ("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", 'bitcoin'),
            ("0x742d35Cc6634C0532925a3b844Bc9e7595f90b36", 'ethereum')
        ]
        
        for test_str, pattern_name in test_cases:
            pattern = patterns[pattern_name]
            self.assertTrue(re.match(pattern, test_str) is not None)
    
    def test_promo_code_patterns(self):
        """Test promo code pattern matching"""
        promo_pattern = r'(?:promo|code|coupon)\s*[:=]\s*([A-Z0-9]{6,20})'
        
        test_cases = [
            "promo: SAVE20NOW",
            "code = DISCOUNT50",
            "coupon: FREESHIPPING"
        ]
        
        for test_str in test_cases:
            match = re.search(promo_pattern, test_str, re.IGNORECASE)
            self.assertIsNotNone(match)
    
    def test_discord_token_pattern(self):
        """Test Discord token pattern matching"""
        discord_pattern = r'[mM][0-9a-zA-Z]{23,25}'
        
        valid_token = "MTAyMzQ1Njc4OTAxMjM0NTY3OQ"
        self.assertTrue(re.match(discord_pattern, valid_token) is not None)
        
        invalid_token = "abc123"
        self.assertFalse(re.match(discord_pattern, invalid_token) is not None)

class TestConfiguration(unittest.TestCase):
    """Test configuration management"""
    
    def test_config_loading(self):
        """Test configuration loading and saving"""
        import configparser
        import tempfile
        
        config = configparser.ConfigParser()
        config['TEST'] = {'key1': 'value1', 'key2': 'value2'}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            config.write(f)
            config_path = f.name
        
        # Reload config
        new_config = configparser.ConfigParser()
        new_config.read(config_path)
        
        self.assertEqual(new_config['TEST']['key1'], 'value1')
        self.assertEqual(new_config['TEST']['key2'], 'value2')
        
        os.remove(config_path)

def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCredentialExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicateDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestFileHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestRegexPatterns))
    suite.addTests(loader.loadTestsFromTestCase(TestConfiguration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == "__main__":
    print("=" * 70)
    print("Running Combo Maker Unit Tests")
    print("=" * 70)
    run_tests()
