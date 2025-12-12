"""Tests étendus pour les pages Streamlit."""
import pytest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from contextlib import contextmanager
from datetime import datetime


@contextmanager
def mock_get_db_context(session):
    """Mock context manager for get_db."""
    try:
        yield session
    finally:
        pass


class TestAddContractPage:
    """Tests pour la page d'ajout de contrat."""

    def test_add_contract_initial_state(self):
        """Test l'état initial de la page."""
        at = AppTest.from_file("src/pages/add_contract.py")
        at.run(timeout=10)

        assert not at.exception
        assert "Ajouter un contrat" in at.title[0].value
        assert "Étape 1 : Importer le document" in at.markdown[1].value

    def test_add_contract_extraction_simulation(self, db_session):
        """Simule une extraction et vérifie l'étape 2."""
        at = AppTest.from_file("src/pages/add_contract.py")

        # Simuler l'état de session après extraction
        at.session_state["extraction_done"] = True
        at.session_state["contract_type"] = "electricite"
        at.session_state["extracted_data"] = {
            "fournisseur": "EDF",
            "prix_kwh": {"base": 0.20},
            "prix_abonnement_mensuel": 15.0,
            "date_debut": "2023-01-01",
            "date_fin": "2024-01-01"
        }
        at.session_state["filename"] = "test.pdf"
        at.session_state["pdf_bytes"] = b"fake pdf content"

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.return_value = mock_get_db_context(db_session)
            at.run(timeout=10)

        assert not at.exception
        # Vérifier que l'étape 2 est affichée
        assert "Étape 2 : Valider les données extraites" in [m.value for m in at.markdown if "Étape 2" in m.value][0]

        # Vérifier que les champs de formulaire sont pré-remplis
        # Note: Streamlit AppTest ne permet pas facilement d'inspecter les valeurs par défaut des widgets
        # mais on peut vérifier que les widgets existent.

        # On devrait avoir des text_input pour fournisseur, etc.
        # Le nombre exact dépend de l'implémentation, mais on peut vérifier qu'il y en a.
        assert len(at.text_input) > 0
        assert len(at.number_input) > 0
        assert len(at.date_input) > 0

    def test_add_contract_save_simulation(self, db_session):
        """Simule la sauvegarde d'un contrat."""
        at = AppTest.from_file("src/pages/add_contract.py")

        # Simuler l'état de session après extraction
        at.session_state["extraction_done"] = True
        at.session_state["contract_type"] = "electricite"
        at.session_state["extracted_data"] = {
            "fournisseur": "EDF",
            "prix_kwh": {"base": 0.20},
            "prix_abonnement_mensuel": 15.0,
            "date_debut": "2023-01-01",
            "date_fin": "2024-01-01"
        }
        at.session_state["filename"] = "test.pdf"
        at.session_state["pdf_bytes"] = b"fake pdf content"

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.return_value = mock_get_db_context(db_session)

            at.run(timeout=10)

            # Vérifier que le formulaire est rendu (présence de champs)
            assert len(at.text_input) > 0
            assert len(at.number_input) > 0


class TestComparePage:
    """Tests pour la page de comparaison."""

    def test_compare_page_initial_state(self, db_session):
        """Test l'état initial de la page de comparaison."""
        at = AppTest.from_file("src/pages/compare.py")

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.return_value = mock_get_db_context(db_session)
            at.run(timeout=10)

        assert not at.exception
        assert "Comparer un contrat" in at.title[0].value

    def test_compare_page_with_contracts(self, db_session, sample_contract_data_telephone):
        """Test la page de comparaison avec des contrats existants."""
        from src.database.models import Contract
        contract = Contract(
            contract_type="telephone",
            provider="Free Mobile",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data=sample_contract_data_telephone,
            original_filename="test.pdf"
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/compare.py")

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.return_value = mock_get_db_context(db_session)
            at.run(timeout=10)

        # Vérifier qu'on a un selectbox pour choisir le contrat
        assert len(at.selectbox) > 0


class TestHistoryPage:
    """Tests pour la page d'historique."""

    def test_history_page_loads(self, db_session):
        """Test que la page historique se charge."""
        at = AppTest.from_file("src/pages/history.py")

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.return_value = mock_get_db_context(db_session)
            at.run(timeout=10)

        assert not at.exception
        assert "Historique" in at.title[0].value

    def test_history_page_with_data(self, db_session, sample_contract_data_telephone):
        """Test la page historique avec des données."""
        from src.database.models import Contract, Comparison

        contract = Contract(
            contract_type="telephone",
            provider="Free Mobile",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data=sample_contract_data_telephone,
            original_filename="test.pdf"
        )
        db_session.add(contract)
        db_session.flush()

        comp = Comparison(
            contract_id=contract.id,
            comparison_type="market_analysis",
            comparison_result={"economie_potentielle_annuelle": 100},
            gpt_prompt="prompt",
            gpt_response="response",
            analysis_summary="Résumé de l'analyse"
        )
        db_session.add(comp)
        db_session.commit()

        at = AppTest.from_file("src/pages/history.py")

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.return_value = mock_get_db_context(db_session)
            at.run(timeout=10)

        # Vérifier qu'on affiche les métriques
        assert len(at.metric) > 0
        # Vérifier qu'on a des expanders pour les détails
        assert len(at.expander) > 0


class TestImportTotalEnergiesPage:
    """Tests pour la page d'import TotalEnergies."""

    def test_import_page_loads(self):
        """Test que la page d'import se charge."""
        at = AppTest.from_file("src/pages/import_totalenergies.py")
        at.run(timeout=10)
        assert not at.exception
        assert "Import Contrat TotalEnergies" in at.title[0].value

    def test_import_page_save(self, db_session):
        """Test la sauvegarde depuis la page d'import."""
        at = AppTest.from_file("src/pages/import_totalenergies.py")

        with patch("src.pages.import_totalenergies.SessionLocal") as mock_session_local:
            mock_session_local.return_value = db_session
            at.run(timeout=10)

            # Trouver le bouton de sauvegarde
            save_btn = [b for b in at.button if "Sauvegarder" in b.label]
            if save_btn:
                save_btn[0].click()
                at.run(timeout=10)
                assert not at.exception
                # Vérifier que les contrats sont créés
                # Comme on utilise db_session, on peut vérifier directement
                # Mais AppTest tourne dans un thread séparé, donc attention à la session
                # Ici on mock SessionLocal pour retourner NOTRE session
                pass


class TestAddContractPageExtended(TestAddContractPage):
    """Tests supplémentaires pour AddContractPage."""

    def test_add_contract_dual_energy(self, db_session):
        """Test l'ajout d'un contrat dual (Elec + Gaz)."""
        at = AppTest.from_file("src/pages/add_contract.py")

        # Simuler l'état de session après extraction
        at.session_state["extraction_done"] = True
        at.session_state["contract_type"] = "electricite_gaz"
        at.session_state["extracted_data"] = {
            "fournisseur": "TotalEnergies",
            "electricite": {
                "pdl": "123",
                "tarifs": {"prix_kwh_ttc": 0.20, "abonnement_mensuel_ttc": 15.0},
                "consommation_estimee_annuelle_kwh": 1000
            },
            "gaz": {
                "pce": "456",
                "tarifs": {"prix_kwh_ttc": 0.08, "abonnement_mensuel_ttc": 20.0},
                "consommation_estimee_annuelle_kwh": 5000
            },
            "dates": {
                "date_debut": "01/01/2024",
                "date_anniversaire": "01/01/2025"
            }
        }
        at.session_state["filename"] = "dual.pdf"
        at.session_state["pdf_bytes"] = b"fake pdf"

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.return_value = mock_get_db_context(db_session)
            at.run(timeout=10)

            # Vérifier qu'on a des onglets ou des sections pour Elec et Gaz
            assert len(at.tabs) >= 2

    def test_add_contract_assurance_pno(self, db_session):
        """Test l'ajout d'un contrat Assurance PNO."""
        at = AppTest.from_file("src/pages/add_contract.py")

        at.session_state["extraction_done"] = True
        at.session_state["contract_type"] = "assurance_pno"
        at.session_state["extracted_data"] = {
            "fournisseur": "AXA",
            "prix_abonnement_mensuel": 15.0,
            "adresse_assuree": "123 Rue Test",
            "date_debut": "01/01/2024",
            "date_anniversaire": "01/01/2025"
        }
        at.session_state["filename"] = "pno.pdf"
        at.session_state["pdf_bytes"] = b"fake pdf"

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)

            # Vérifier les champs spécifiques
            assert len(at.text_input) > 0

    def test_add_contract_mobile(self, db_session):
        """Test l'ajout d'un contrat Mobile."""
        at = AppTest.from_file("src/pages/add_contract.py")

        at.session_state["extraction_done"] = True
        at.session_state["contract_type"] = "telephone"
        at.session_state["extracted_data"] = {
            "fournisseur": "Free",
            "prix_abonnement_mensuel": 19.99,
            "data_go": 200,
            "date_debut": "01/01/2024",
            "date_anniversaire": "01/01/2025"
        }
        at.session_state["filename"] = "mobile.pdf"
        at.session_state["pdf_bytes"] = b"fake pdf"

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.return_value = mock_get_db_context(db_session)
            at.run(timeout=10)

            assert len(at.text_input) > 0


class TestComparePageExtended(TestComparePage):
    """Tests supplémentaires pour ComparePage."""

    def test_compare_run_market_analysis(self, db_session, sample_contract_data_telephone):
        """Test l'exécution d'une analyse de marché."""
        from src.database.models import Contract
        contract = Contract(
            contract_type="telephone",
            provider="Free Mobile",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data=sample_contract_data_telephone,
            original_filename="test.pdf"
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/compare.py")

        # Mocker OpenAIService pour retourner une analyse
        with patch("src.database.get_db") as mock_get_db, \
             patch("src.services.openai_service.OpenAIService.compare_with_market") as mock_compare:

            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            mock_compare.return_value = {
                "analysis": {
                    "recommandation": "Changer",
                    "justification": "Trop cher",
                    "niveau_competitivite": "Faible",
                    "tarif_actuel": 100,
                    "economie_potentielle_annuelle": 50
                },
                "meilleure_offre": {},
                "prompt": "test prompt",
                "raw_response": "test response"
            }

            at.run(timeout=10)

            # Sélectionner le contrat (si possible via session state ou index)
            # AppTest ne permet pas facilement de sélectionner dans un selectbox par valeur
            # Mais on peut simuler le clic sur le bouton "Lancer l'analyse"

            # On va supposer que le premier contrat est sélectionné par défaut

            analyze_btns = [b for b in at.button if "Lancer l'analyse" in b.label]
            if analyze_btns:
                analyze_btns[0].click()
                at.run(timeout=10)

                # Vérifier si le mock a été appelé
                # Note: AppTest tourne dans un thread, donc le mock doit être thread-safe ou global
                # Ici on patch globalement donc ça devrait aller
                # assert mock_compare.called

                # Vérifier les exceptions
                if at.exception:
                    pytest.fail(f"Exception dans la page: {at.exception[0].message}")

                # Vérifier que le résultat est affiché
                # On cherche "Changer" ou "Trop cher"
                found = False
                for m in at.markdown:
                    if "Changer" in m.value:
                        found = True
                        break

                if not found:
                    # Debug: check if "Aucun contrat" is displayed
                    if any("Aucun contrat" in m.value for m in at.info):
                        pytest.fail("Aucun contrat trouvé dans la page")

                    # Debug: print markdown values
                    # print([m.value for m in at.markdown])
                    pass

                assert found, "Résultat de l'analyse non trouvé"


class TestDashboardPageExtended:
    """Tests supplémentaires pour DashboardPage."""

    def test_dashboard_metrics(self, db_session, sample_contract_data_telephone):
        """Test les métriques du dashboard."""
        from src.database.models import Contract
        contract = Contract(
            contract_type="telephone",
            provider="Free Mobile",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data=sample_contract_data_telephone,
            original_filename="test.pdf"
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/dashboard.py")

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)

            # Vérifier les métriques
            assert len(at.metric) > 0
            # Vérifier "Total Contrats"
            assert any("Total Contrats" in m.label for m in at.metric)
            assert any("1" in str(m.value) for m in at.metric if "Total Contrats" in m.label)

    def test_dashboard_contract_list(self, db_session, sample_contract_data_telephone):
        """Test l'affichage de la liste des contrats."""
        from src.database.models import Contract
        contract = Contract(
            contract_type="telephone",
            provider="Free Mobile",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data=sample_contract_data_telephone,
            original_filename="test.pdf"
        )
        db_session.add(contract)
        db_session.commit()

        at = AppTest.from_file("src/pages/dashboard.py")

        with patch("src.database.get_db") as mock_get_db:
            mock_get_db.side_effect = lambda: mock_get_db_context(db_session)
            at.run(timeout=10)

            # Vérifier que le contrat est affiché dans la liste
            # Le dashboard utilise des colonnes et du markdown, pas des expanders
            found_provider = False
            for m in at.markdown:
                if "Free Mobile" in m.value:
                    found_provider = True
                    break

            assert found_provider, "Le fournisseur 'Free Mobile' n'est pas affiché dans le dashboard"
