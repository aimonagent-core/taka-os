"""Templates HTML pour les emails."""


def _base_template(title: str, content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #fff; padding: 2rem; border-radius: 8px; }}
        .header {{ border-bottom: 3px solid #2563eb; padding-bottom: 1rem; margin-bottom: 1.5rem; }}
        .header h1 {{ color: #2563eb; margin: 0; font-size: 1.5rem; }}
        .footer {{ margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e5e5; font-size: 0.85rem; color: #666; }}
        .btn {{ display: inline-block; background: #2563eb; color: #fff; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 6px; font-weight: 600; }}
        .alert-box {{ background: #eff6ff; border-left: 4px solid #2563eb; padding: 1rem; margin: 1rem 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>TAKA OS</h1>
        </div>
        {content}
        <div class="footer">
            <p>TAKA OS — Plateforme d'appels d'offres automatises</p>
            <p>Si vous avez des questions, contactez-nous a contact@taka-os.com</p>
        </div>
    </div>
</body>
</html>"""


def welcome_template(user_name: str) -> str:
    content = f"""
    <h2>Bienvenue, {user_name} !</h2>
    <p>Votre compte TAKA OS est maintenant actif. Vous pouvez commencer a explorer les appels d'offres qui correspondent a votre activite.</p>
    <div class="alert-box">
        <strong>Prochaines etapes :</strong>
        <ul>
            <li>Configurez votre premiere ligne metier</li>
            <li>Activez la veille automatisee</li>
            <li>Personnalisez vos alertes email</li>
        </ul>
    </div>
    <p><a href="https://app.taka-os.com/veille" class="btn">Acceder a la veille</a></p>
    """
    return _base_template("Bienvenue sur TAKA OS", content)


def payment_confirmation_template(plan_name: str, amount: str) -> str:
    content = f"""
    <h2>Confirmation de paiement</h2>
    <p>Merci pour votre souscription au plan <strong>{plan_name}</strong>.</p>
    <div class="alert-box">
        <p>Montant facture : <strong>{amount}</strong></p>
        <p>Statut : <strong>Paye</strong></p>
    </div>
    <p>Votre acces est immediatement actif. Vous pouvez gerer votre souscription depuis votre espace client.</p>
    <p><a href="https://app.taka-os.com/subscription" class="btn">Gerer ma souscription</a></p>
    """
    return _base_template("Confirmation de paiement", content)


def daily_alert_template(aos_count: int, ao_list_html: str) -> str:
    content = f"""
    <h2>Votre veille du jour</h2>
    <p>Nous avons detecte <strong>{aos_count}</strong> nouveaux appels d'offres correspondant a vos criteres.</p>
    {ao_list_html}
    <p><a href="https://app.taka-os.com/veille" class="btn">Voir tous les AO</a></p>
    """
    return _base_template("Veille quotidienne TAKA OS", content)


def subscription_cancelled_template(plan_name: str) -> str:
    content = f"""
    <h2>Souscription annulee</h2>
    <p>Votre souscription au plan <strong>{plan_name}</strong> a ete annulee.</p>
    <div class="alert-box">
        <p>Votre compte est revenu au plan <strong>Free</strong>. Vous conservez l'acces a vos donnees mais avec des limites reduites.</p>
    </div>
    <p>Si vous changez d'avis, vous pouvez reactiver votre souscription a tout moment.</p>
    <p><a href="https://app.taka-os.com/pricing" class="btn">Voir les plans</a></p>
    """
    return _base_template("Souscription annulee", content)
