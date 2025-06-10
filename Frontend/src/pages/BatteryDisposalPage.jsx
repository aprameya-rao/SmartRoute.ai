import React from 'react';
import './BatteryDisposalPage.css';

function BatteryDisposalPage() {
  return (
    <div className="battery-disposal-page">
      <h1>EV Battery Disposal Information</h1>

      <section className="disposal-intro">
        <p>Proper disposal of Electric Vehicle (EV) batteries is crucial for environmental protection and resource recovery. EV batteries contain valuable materials like lithium, cobalt, and nickel, which can be recycled, and hazardous components that must be managed responsibly.</p>
      </section>

      <section className="regulations-india">
        <h2>Regulatory Framework in India</h2>
        <p>In India, the disposal and recycling of batteries, including EV batteries, are primarily governed by the <strong>Battery Waste Management Rules, 2022</strong>. Key aspects include:</p>
        <ul>
          <li><strong>Extended Producer Responsibility (EPR):</strong> Producers (manufacturers and importers) are responsible for the collection and recycling of batteries, meeting specific collection targets.</li>
          <li><strong>Centralized Online Portal:</strong> The Central Pollution Control Board (CPCB) has developed a centralized online portal for registration and reporting by producers, recyclers, and refurbishers.</li>
          <li><strong>Recycling Targets:</strong> The rules mandate specific recycling efficiencies and targets for various battery types.</li>
          <li><strong>Prohibition of Landfilling:</strong> Batteries are prohibited from being landfilled or incinerated.</li>
          <li><strong>Recent Amendments:</strong> The <strong>Battery Waste Management (Second Amendment) Rules 2024</strong> introduced provisions for minimum recycled material use in new batteries, promoting a circular economy.</li>
        </ul>
        <p>For more detailed information, refer to the official documents from the Ministry of Environment, Forest and Climate Change (MoEFCC) and the Central Pollution Control Board (CPCB).</p>
      </section>

      <section className="how-to-dispose">
        <h2>How to Safely Dispose of EV Batteries</h2>
        <p><strong>Never dispose of EV batteries in regular waste bins.</strong> Always contact authorized channels:</p>
        <ol>
          <li><strong>Vehicle Manufacturer/Dealer:</strong> Your EV manufacturer or authorized service center is typically the first point of contact. They have established channels for battery return and recycling.</li>
          <li><strong>Authorized Recyclers:</strong> Look for companies specifically authorized by the CPCB for battery recycling. These facilities have the necessary infrastructure to safely dismantle and process EV batteries.</li>
          <li><strong>Producer Responsibility Organizations (PROs):</strong> Some producers work with PROs to manage their EPR obligations, which include collecting used batteries.</li>
        </ol>
      </section>

      <section className="recycling-companies-india">
        <h2>Key EV Battery Recycling Companies in India</h2>
        <p>Here are some of the prominent companies involved in EV battery recycling and materials recovery in India:</p>
        <ul>
          <li><strong>Attero Recycling:</strong> One of India's largest e-waste and battery recycling companies, active in lithium-ion battery recycling.</li>
          <li><strong>Tata Chemicals:</strong> Involved in the development of lithium-ion battery recycling technologies.</li>
          <li><strong>Gravita India:</strong> Specializes in lead recycling, but expanding into lithium-ion battery recycling.</li>
          <li><strong>LOHUM:</strong> Focuses on repurposing and recycling lithium-ion batteries.</li>
          <li><strong>RecycleKaro:</strong> A growing player in battery waste management and recycling.</li>
          <li><strong>Exide Industries:</strong> A major battery manufacturer, also exploring recycling solutions.</li>
        </ul>
      </section>

      <section className="second-life">
        <h2>Second Life Applications</h2>
        <p>Before full recycling, EV batteries often have a "second life." Even after their capacity drops below the optimal level for vehicles, they can still be highly effective for:</p>
        <ul>
          <li><strong>Stationary Energy Storage:</strong> Used in homes, businesses, or grid-scale applications to store renewable energy (solar, wind) or provide backup power.</li>
          <li><strong>Telecommunications Towers:</strong> Providing power backup for mobile towers.</li>
          <li><strong>E-Rickshaws and Low-Speed EVs:</strong> Sometimes repurposed for less demanding electric vehicles.</li>
        </ul>
        <p>This extends the useful life of batteries, reducing the demand for new materials and environmental impact.</p>
      </section>

      <section className="faqs">
        <h2>Frequently Asked Questions</h2>
        <dl>
          <dt>What is the average lifespan of an EV battery?</dt>
          <dd>Most EV batteries are designed to last 8-10 years or 160,000-240,000 km, though performance degrades gradually.</dd>

          <dt>Can I sell my old EV battery?</dt>
          <dd>It's best to return it through authorized channels (manufacturer or certified recycler) rather than selling it informally, to ensure proper and safe handling.</dd>

          <dt>Are EV batteries environmentally friendly?</dt>
          <dd>While manufacturing has an impact, their full lifecycle environmental footprint, especially with proper recycling, is significantly lower than internal combustion engine vehicles, primarily due to zero tailpipe emissions.</dd>
        </dl>
      </section>
    </div>
  );
}

export default BatteryDisposalPage;