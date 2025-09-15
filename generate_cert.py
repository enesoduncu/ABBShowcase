#!/usr/bin/env python3
"""
SSL-Zertifikatsgenerator für ABB Streamlit
Generiert selbstsignierte Zertifikate für die Testumgebung
"""

import os
import ssl
import socket
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from pathlib import Path

def generate_self_signed_cert():
    """Generiert ein selbstsigniertes SSL-Zertifikat"""
    
    # Verzeichnis für Zertifikate erstellen
    cert_dir = Path("ssl_certs")
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # Private Key generieren
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Zertifikat generieren
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Baden-Wuerttemberg"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Stuttgart"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "IHK Region Stuttgart"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Zertifikat speichern
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # Private Key speichern
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    print(f"✅ SSL-Zertifikat erfolgreich generiert!")
    print(f"📁 Zertifikat: {cert_file}")
    print(f"🔑 Private Key: {key_file}")
    print(f"⏰ Gültig bis: {cert.not_valid_after}")
    
    return str(cert_file), str(key_file)

def create_env_file(cert_file, key_file):
    """Erstellt eine .env-Datei mit HTTPS-Konfiguration"""
    
    env_content = f"""# HTTPS-Konfiguration für Testumgebung
ENABLE_HTTPS=True
SSL_CERT_FILE={cert_file}
SSL_KEY_FILE={key_file}

# Andere Sicherheitseinstellungen
SECURITY_ENABLED=True
DEBUG=True
MIN_PASSWORD_LENGTH=12
SESSION_TIMEOUT_HOURS=8
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
FORCE_PASSWORD_CHANGE_DAYS=90
REQUIRE_STRONG_PASSWORDS=True

# Logging
ENABLE_SECURITY_LOGGING=True
LOG_LEVEL=INFO
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"✅ .env-Datei mit HTTPS-Konfiguration erstellt!")

def main():
    """Hauptfunktion"""
    print("🔐 SSL-Zertifikatsgenerator für ABB Streamlit")
    print("=" * 50)
    
    try:
        # Zertifikat generieren
        cert_file, key_file = generate_self_signed_cert()
        
        # .env-Datei erstellen
        create_env_file(cert_file, key_file)
        
        print("\n🎉 HTTPS ist jetzt konfiguriert!")
        print("\n📋 Nächste Schritte:")
        print("1. Stoppen Sie die aktuelle Streamlit-Anwendung (Ctrl+C)")
        print("2. Starten Sie sie neu mit: streamlit run app.py")
        print("3. Die Anwendung läuft jetzt über HTTPS")
        print("4. Browser-Warnung über selbstsigniertes Zertifikat bestätigen")
        
    except Exception as e:
        print(f"❌ Fehler bei der Zertifikatsgenerierung: {e}")
        print("Stellen Sie sicher, dass cryptography installiert ist:")
        print("pip install cryptography")

if __name__ == "__main__":
    main()
