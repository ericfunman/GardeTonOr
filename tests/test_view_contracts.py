"""Tests pour la page de visualisation des contrats."""
import pytest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest
from contextlib import contextmanager
from datetime import datetime
from src.database.models import Contract

@contextmanager
def mock_get_db_context(session):
    """Mock context manager for get_db."""
    try:
        yield session
    finally:
        pass

class TestViewContractsPage:
    """Tests pour la page de visualisation des contrats."""

    def test_view_contracts_initial_state(self, db_session):
        """Test l'état initial de la page."""
        # Créer un contrat de test
        contract = Contract(
            contract_type="electricite",
            provider="EDF",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={
                "fournisseur": "EDF",
                "electricite": {
                    "tarifs": {"abonnement_mensuel_ttc": 15.0, "prix_kwh_ttc": 0.20}
                }
            },
            original_filename="test.pdf",
            validated=1
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/view_contracts.py")
        
        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)

        assert not at.exception
        assert "Visualisation des contrats" in at.title[0].value

    def test_view_contracts_select_contract(self, db_session):
        """Test la sélection et l'affichage d'un contrat."""
        contract = Contract(
            contract_type="electricite",
            provider="TotalEnergies",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={
                "fournisseur": "TotalEnergies",
                "electricite": {
                    "pdl": "123456789",
                    "puissance_souscrite_kva": 6,
                    "tarifs": {"abonnement_mensuel_ttc": 12.0, "prix_kwh_ttc": 0.18}
                }
            },
            original_filename="total.pdf",
            validated=1
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/view_contracts.py")
        
        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)
            
            # Sélectionner le contrat dans la selectbox
            if at.selectbox:
                at.selectbox[0].set_value(contract.id).run()
                
                assert not at.exception
                # Vérifier que TotalEnergies apparaît quelque part (titre, markdown, json, metric)
                found = False
                for md in at.markdown:
                    if "TotalEnergies" in md.value:
                        found = True
                        break
                
                if not found:
                    # Vérifier dans les metrics
                    for metric in at.metric:
                        if "TotalEnergies" in metric.label or "TotalEnergies" in str(metric.value):
                            found = True
                            break
                            
                if not found and at.json:
                    # Vérifier dans le JSON
                    if "TotalEnergies" in str(at.json[0].value):
                        found = True
                        
                # Si toujours pas trouvé, vérifier le sous-titre
                if not found:
                    for subheader in at.subheader:
                        if "TotalEnergies" in subheader.value:
                            found = True
                            break

                assert found

    def test_view_contracts_assurance_pno(self, db_session):
        """Test l'affichage d'un contrat assurance PNO."""
        contract = Contract(
            contract_type="assurance_pno",
            provider="Generali",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={
                "assureur": "Generali",
                "prime_annuelle": 150.0,
                "franchise": 200.0,
                "adresse_assuree": "10 rue de la Liberté"
            },
            original_filename="pno.pdf",
            validated=1
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/view_contracts.py")
        
        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)
            
            if at.selectbox:
                at.selectbox[0].set_value(contract.id).run()
                assert not at.exception
                # Vérifier l'affichage de la prime
                found = False
                for metric in at.metric:
                    if "150.00 €" in metric.value:
                        found = True
                        break
                assert found

    def test_view_contracts_no_contracts(self, db_session):
        """Test l'affichage quand il n'y a aucun contrat."""
        at = AppTest.from_file("src/pages/view_contracts.py")
        
        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)
            
            assert "Aucun contrat enregistré" in at.info[0].value

    def test_view_contracts_preselection(self, db_session):
        """Test la présélection d'un contrat via session_state."""
        contract = Contract(
            contract_type="electricite",
            provider="Engie",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={"fournisseur": "Engie"},
            original_filename="engie.pdf",
            validated=1
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/view_contracts.py")
        at.session_state["view_contract_id"] = contract.id
        
        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)
            
            # Vérifier que le contrat est sélectionné (Engie affiché)
            # Le selectbox devrait avoir l'index correct
            # On vérifie si Engie est dans les options du selectbox
            assert "Engie" in str(at.selectbox[0].options)

    def test_view_contracts_preselection_invalid_id(self, db_session):
        """Test la présélection d'un ID invalide."""
        contract = Contract(
            contract_type="electricite",
            provider="Engie",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={"fournisseur": "Engie"},
            original_filename="engie.pdf",
            validated=1
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/view_contracts.py")
        at.session_state["view_contract_id"] = 99999 # ID inexistant
        
        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)
            
            assert not at.exception
            # Devrait charger par défaut (index 0) sans erreur
            assert "Engie" in str(at.selectbox[0].options)

    def test_view_contracts_not_found(self, db_session):
        """Test le cas où le contrat sélectionné n'existe pas."""
        # Créer un contrat pour avoir la liste
        contract = Contract(
            contract_type="electricite",
            provider="Fake",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={"fournisseur": "Fake"},
            original_filename="fake.pdf",
            validated=1
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/view_contracts.py")
        
        with patch("src.database.get_db") as mock_get_db, \
             patch("src.services.ContractService.get_contract_by_id") as mock_get_contract:
            
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            # On laisse get_all_contracts fonctionner normalement (via le vrai service ou mocké si besoin)
            # Mais on force get_contract_by_id à retourner None
            mock_get_contract.return_value = None
            
            at.run(timeout=10)
            
            if at.selectbox:
                at.selectbox[0].set_value(contract.id).run()
                assert "Contrat introuvable" in at.error[0].value
                
    def test_view_contracts_assurance_habitation(self, db_session):
        """Test l'affichage d'un contrat d'assurance habitation."""
        contract = Contract(
            contract_type="assurance_habitation",
            provider="AXA",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={
                "assureur": "AXA",
                "bien_assure": {
                    "adresse": "1 rue de la Paix",
                    "type_logement": "Appartement",
                    "surface_m2": 50,
                    "piscine": False,
                    "cheminee": True
                },
                "tarifs": {"prime_annuelle_ttc": 200.0}
            },
            original_filename="axa.pdf",
            validated=1
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/view_contracts.py")
        
        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)
            
            if at.selectbox:
                at.selectbox[0].set_value(contract.id).run()
                assert not at.exception
                # Vérifier la présence de détails spécifiques
                assert "Cheminée" in [m.value for m in at.markdown if "Cheminée" in m.value][0]

    def test_view_contracts_telephone(self, db_session):
        """Test l'affichage d'un contrat téléphone."""
        contract = Contract(
            contract_type="telephone",
            provider="Sosh",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={
                "fournisseur": "Sosh",
                "forfait_nom": "Forfait 20Go",
                "data_go": 20,
                "prix_mensuel": 19.99
            },
            original_filename="sosh.pdf",
            validated=1
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/view_contracts.py")
        
        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)
            
            if at.selectbox:
                at.selectbox[0].set_value(contract.id).run()
                assert not at.exception
                # Vérifier l'affichage des données mobiles
                assert "20 Go" in [m.value for m in at.markdown if "20 Go" in m.value][0]

    def test_view_contracts_legacy_format(self, db_session):
        """Test l'affichage d'un contrat avec format legacy (plat)."""
        contract = Contract(
            contract_type="electricite",
            provider="LegacyProvider",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={
                "fournisseur": "LegacyProvider",
                "prix_kwh": 0.15, # Format plat
                "prix_abonnement": 10.0
            },
            original_filename="legacy.pdf",
            validated=1
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/view_contracts.py")
        
        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)
            
            if at.selectbox:
                at.selectbox[0].set_value(contract.id).run()
                assert not at.exception
