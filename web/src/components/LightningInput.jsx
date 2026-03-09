import { useState } from "react";

function LightningInput({ onSubmit, submitLabel = "Ajouter l’éclair" }) {
  const [form, setForm] = useState({
    date: "",
    lat: "",
    lon: "",
    amplitude: "",
    maxis: "",
    icloud: "false"
  });

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: value
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    if (!form.date || !form.lat || !form.lon || !form.amplitude) {
      alert("Remplis au moins date, latitude, longitude et amplitude.");
      return;
    }

    const formattedEvent = {
      date: form.date,
      lat: Number(form.lat),
      lon: Number(form.lon),
      amplitude: Number(form.amplitude),
      maxis: form.maxis === "" ? null : Number(form.maxis),
      icloud: form.icloud === "true"
    };

    onSubmit(formattedEvent);

    setForm({
      date: "",
      lat: "",
      lon: "",
      amplitude: "",
      maxis: "",
      icloud: "false"
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
        Latitude
        <input
          type="number"
          step="any"
          name="lat"
          value={form.lat}
          onChange={handleChange}
        />
      </label>

      <label>
        Longitude
        <input
          type="number"
          step="any"
          name="lon"
          value={form.lon}
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
        Type icloud
        <select name="icloud" value={form.icloud} onChange={handleChange}>
          <option value="false">false</option>
          <option value="true">true</option>
        </select>
      </label>

      <button type="submit">{submitLabel}</button>
    </form>
  );
}

export default LightningInput;