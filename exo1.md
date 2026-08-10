# 📋 Exercice 1 - API de gestion de tâches avec FastAPI

Création d'une API RESTful de gestion de tâches avec **FastAPI**, **SQLAlchemy** et gestion d'envois d'e-mails.

---

## 🗄️ Modèle de données (`sqlalchemy`)

### Modèle `Task`
* **`id`** : `Integer` (Clé primaire, auto-incrémentée)
* **`name`** : `String` (Nom de la tâche)
* **`attribution_email`** : `String` (Email de la personne assignée)
* **`status`** : `Enum` / `String` (Valeurs possibles : `in_progress`, `done` — *Par défaut : `in_progress`*)
* **`start_date`** : `DateTime` (Date de création / début — *Générée automatiquement à `now()`*)
* **`end_date`** : `DateTime` (Date d'échéance — *Calculée lors de la création : `start_date + duration`*)

---

## 🚀 Contrôleur `TaskController` (`/tasks`)

### 1. Créer une tâche
* **Endpoint** : `POST /tasks`
* **Paramètres d'entrée** (Body/Schema Pydantic) :
  * `name` : `str`
  * `attribution_email` : `EmailStr`
  * `duration` : `int` (Nombre de jours pour réaliser la tâche)
* **Comportement & Logique métier** :
  * Définir `status` par défaut à `in_progress`.
  * Calculer `end_date` à partir de `start_date + duration`.
  * Sauvegarder la tâche en base de données.
  * **Email** : Envoyer un e-mail de notification à `attribution_email` pour l'informer de la nouvelle tâche.
* **Erreurs HTTP** :
  * `422 Unprocessable Entity` : Données d'entrée invalides (ex. email non valide, durée négative).

---

### 2. Lister / Filtrer les tâches
* **Endpoint** : `GET /tasks`
* **Paramètres de requête** (Query parameters) :
  * `email` : `str` *(Optionnel - Filtrer par destinataire)*
  * `status` : `str` *(Optionnel - Filtrer par `in_progress` ou `done`)*
  * `page` : `int` *(Optionnel - Par défaut : `1`, min : `1`)*
  * `limit` : `int` *(Optionnel - Par défaut : `10`, max : `100`)*
* **Comportement** :
  * Retourne la liste des tâches paginée et filtrée selon les critères fournis.

---

### 3. Modifier le statut d'une tâche
* **Endpoint** : `PUT /tasks/{id}`
* **Paramètres d'entrée** :
  * `id` : `int` *(Path parameter)*
  * `status` : `str` *(Body parameter : `in_progress` ou `done`)*
* **Comportement & Logique métier** :
  * **Règle de gestion** : La modification du statut est autorisée **uniquement si la date actuelle n'a pas dépassé la date d'échéance (`now() <= end_date`)**.
* **Erreurs HTTP** :
  * `404 Not Found` : Si la tâche correspondant à l'ID n'existe pas en base de données.
  * `400 Bad Request` : Si la date d'échéance est dépassée (`now() > end_date`).

---

### 4. Supprimer une tâche
* **Endpoint** : `DELETE /tasks/{id}`
* **Paramètres d'entrée** :
  * `id` : `int` *(Path parameter)*
* **Comportement & Logique métier** :
  * **Règle de gestion** : Une tâche ne **peut pas** être supprimée si son statut est `done`.
  * Si le statut est `in_progress` :
    * Supprimer la tâche de la base de données.
    * **Email** : Envoyer un e-mail à `attribution_email` pour notifier de l'annulation/suppression de la tâche.
* `404 Not Found` : Si la tâche correspondant à l'ID n'existe pas en base de données.
* `400 Bad Request` : Si la tâche est au statut `done`.

---

## 👥 Modèle `Employe`

* **`id`** : `int`
* **`last_name`** : `str`
* **`first_name`** : `str`
* **`email`** : `str`
* **`salary`** : `decimal`
* **`titre`** : `Enum` (`PM`, `DEV`)
* **`supervisor_id`** : `int | null` (référence vers un autre employé)

### Règles métier

* Seuls les `DEV` peuvent avoir des tâches.
* Un `DEV` doit avoir un `supervisor`.
* Un `PM` ne peut pas être supervisé par un `DEV`.
* Toute modification de supervision doit être cohérente et ne pas créer de cycle.

### Cas d’usage

1. **Créer un `EMPLOYE`**
   * Ajouter l’employé avec un `supervisor` valide.

2. **Supprimer un `DEV`**
   * Toutes les tâches et les employés qui lui étaient attribués sont réaffectés à son `supervisor`.
   * Si un employé n’a pas de superviseur, la suppression n’est pas autorisée.

3. **Modifier le superviseur**
   * Changer le `supervisor` avec `idEmploye` et `idSuperviseur`.
   * Vérifier l’absence de cycle de supervision.

### Notification par e-mail

* Lors des changements importants, envoyer un e-mail à toute la hiérarchie concernée.
* Par exemple, à la création, suppression ou réaffectation d’un `DEV`.



