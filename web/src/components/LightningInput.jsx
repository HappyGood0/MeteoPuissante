import { useState } from "react";

function LightningInput({ onSubmit, submitLabel = "Ajouter l’éclair" }) {
  const [form, setForm] = useState({
    date: "",
    dist: "",
    azimuth: "",
    amplitude: "",
    maxis: "",
    icloud: false
  });

  function handleChange(event) {
    const { name, value, type, checked } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    if (!form.date || form.dist === "" || form.azimuth === "" || !form.amplitude) {
      alert("Remplis au moins date, distance, azimut et amplitude.");
      return;
    }

    const formattedEvent = {
      date: form.date,
      dist: Number(form.dist),
      azimuth: Number(form.azimuth),
      amplitude: Number(form.amplitude),
      maxis: form.maxis === "" ? null : Number(form.maxis),
      icloud: form.icloud
    };

    onSubmit(formattedEvent);

    setForm({
      date: "",
      dist: "",
      azimuth: "",
      amplitude: "",
      maxis: "",
      icloud: false
    });
  }

  return (
    <form className="card form-block" onSubmit={handleSubmit}>
      <h3>Saisie manuelle</h3>

      <label>
        Date / heure
        <input
          type="datetime-local"
          name="date"
          value={form.date}
          onChange={handleChange}
        />
      </label>

      <label>
        Distance à l’aéroport
        <input
          type="number"
          step="any"
          name="dist"
          value={form.dist}
          onChange={handleChange}
        />
      </label>

      <label>
        Azimut
        <input
          type="number"
          step="any"
          name="azimuth"
          value={form.azimuth}
          onChange={handleChange}
        />
      </label>

      <label>
        Amplitude
        <input
          type="number"
          step="any"
          name="amplitude"
          value={form.amplitude}
          onChange={handleChange}
        />
      </label>

      <label>
        Maxis
        <input
          type="number"
          step="any"
          name="maxis"
          value={form.maxis}
          onChange={handleChange}
        />
      </label>

      <label>
        <input
          type="checkbox"
          name="icloud"
          checked={form.icloud}
          onChange={handleChange}
        />
        Éclair intra-nuage
      </label>

      <button type="submit">{submitLabel}</button>
    </form>
  );
}

export default LightningInput;